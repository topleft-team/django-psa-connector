import logging

from django.utils import timezone
from django.db import transaction, IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from dateutil.parser import parse

from djpsa.api.client import APIClient
from djpsa.sync.models import SyncJob
from djpsa.halo import models

logger = logging.getLogger(__name__)

CREATED = 1
UPDATED = 2
SKIPPED = 3


def log_sync_job(f):
    def wrapper(*args, **kwargs):
        sync_instance = args[0]
        created_count = updated_count = deleted_count = skipped_count = 0
        sync_job = SyncJob()
        sync_job.start_time = timezone.now()
        sync_job.entity_name = sync_instance.model_class.__bases__[0].__name__
        sync_job.synchronizer_class = \
            sync_instance.__class__.__name__

        if sync_instance.full:
            sync_job.sync_type = 'full'
        else:
            sync_job.sync_type = 'partial'

        sync_job.save()

        try:
            created_count, updated_count, skipped_count, deleted_count = \
                f(*args, **kwargs)
            sync_job.success = True
        except Exception as e:
            sync_job.message = str(e.args[0])
            sync_job.success = False
            raise
        finally:
            sync_job.end_time = timezone.now()
            sync_job.added = created_count
            sync_job.updated = updated_count
            sync_job.skipped = skipped_count
            sync_job.deleted = deleted_count
            sync_job.save()

        return created_count, updated_count, skipped_count, deleted_count
    return wrapper


class InvalidObjectException(Exception):
    """
    If for any reason an object can't be created (for example, it references
    an unknown foreign object, or is missing a required field), raise this
    so that the synchronizer can catch it and continue with other records.
    """
    pass


class SyncResults:
    """Track results of a sync job."""
    def __init__(self):
        self.created_count = 0
        self.updated_count = 0
        self.skipped_count = 0
        self.deleted_count = 0
        self.synced_ids = set()


class Synchronizer:
    lookup_key = 'id'
    model_class = None

    def __init__(self, full=False):
        self.full = full

    @log_sync_job
    def sync(self):
        results = SyncResults()
        results = self.fetch_records(results)

        if self.full:
            # Set of IDs of all records prior to sync,
            # to find stale records for deletion.
            initial_ids = self._instance_ids()

            results.deleted_count = self.prune_stale_records(
                initial_ids, results.synced_ids
            )

        return results.created_count, results.updated_count, \
            results.skipped_count, results.deleted_count

    def _instance_ids(self):
        ids = self.model_class.objects.all().order_by('id')\
            .values_list('id', flat=True)
        return set(ids)

    def fetch_records(self, results, conditions=None):
        """
        For all pages of results, save each page of results to the DB.

        If conditions is supplied in the call, then use only those conditions
        while fetching pages of records. If it's omitted, then use
        self.api_conditions.
        """

        client = APIClient(self.endpoint, self.params)

        page = 1
        while True:
            logger.info(
                'Fetching {} records, batch {}'.format(
                    self.model_class.__bases__[0].__name__, page)
            )
            response = client.request(params={
                'page_no': page,
            })
            records = self._unpack_records(response)
            self.persist_page(records, results)
            page += 1
            if len(records) < 50:
                # This page wasn't full, so there's no more records after
                # this page.
                break
        return results

    def persist_page(self, records, results):
        """Persist one page of records to DB."""
        for record in records:
            try:
                with transaction.atomic():
                    instance, result = self.update_or_create_instance(record)
                if result == CREATED:
                    results.created_count += 1
                elif result == UPDATED:
                    results.updated_count += 1
                else:
                    results.skipped_count += 1
            except (IntegrityError, InvalidObjectException) as e:
                logger.warning('{}'.format(e))

            results.synced_ids.add(record[self.lookup_key])

        return results

    def set_relations(self, instance, json_data):
        for json_field, value in self.related_meta.items():
            model_class, field_name = value
            self._assign_relation(
                instance,
                json_data,
                json_field,
                model_class,
                field_name
            )

    def _assign_field_data(self, instance, api_instance):
        raise NotImplementedError

    def _unpack_records(self, response):
        records = response.json()[self.response_key]
        return records

    @staticmethod
    def _assign_null_relation(instance, model_field):
        """
        Set the FK to null, but handle issues like the FK being non-null.

        This can happen because ConnectWise gives us records that point to
        non-existent records- such as activities whose assignTo fields point
        to deleted members.
        """
        try:
            setattr(instance, model_field, None)
        except ValueError:
            # The model_field may have been non-null.
            raise InvalidObjectException(
                "Unable to set field {} on {} to null, as it's required.".
                format(model_field, instance)
            )

    def _assign_relation(self, instance, json_data,
                         json_field, model_class, model_field):
        """
        Look up the given foreign relation, and set it to the given
        field on the instance.
        """
        relation_id = json_data.get(json_field)
        if relation_id is None:
            self._assign_null_relation(instance, model_field)
            return

        uid = relation_id

        try:
            related_instance = model_class.objects.get(pk=uid)
            setattr(instance, model_field, related_instance)
        except model_class.DoesNotExist:
            logger.warning(
                'Failed to find {} {} for {} {}.'.format(
                    json_field,
                    uid,
                    type(instance),
                    instance.id
                )
            )
            self._assign_null_relation(instance, model_field)

    def update_or_create_instance(self, api_instance):
        """
        Creates and returns an instance if it does not already exist.
        """
        result = None
        try:
            instance_pk = api_instance[self.lookup_key]
            instance = self.model_class.objects.get(pk=instance_pk)
        except self.model_class.DoesNotExist:
            instance = self.model_class()
            result = CREATED

        try:
            self._assign_field_data(instance, api_instance)

            # Tracking skipped records not implemented
            if result == CREATED:
                instance.save()
            elif result is None:
                instance.save()
                result = UPDATED
            else:
                result = SKIPPED
        except AttributeError as e:
            msg = "AttributeError while attempting to sync object {}." \
                  " Error: {}".format(self.model_class, e)
            logger.error(msg)
            raise InvalidObjectException(msg)
        except IntegrityError as e:
            msg = "IntegrityError while attempting to create {}." \
                  " Error: {}".format(self.model_class, e)
            logger.error(msg)
            raise InvalidObjectException(msg)

        if result == CREATED:
            result_log = 'Created'
        elif result == UPDATED:
            result_log = 'Updated'
        else:
            result_log = 'Skipped'

        logger.info('{}: {} {}'.format(
            result_log,
            self.model_class.__bases__[0].__name__,
            instance
        ))

        return instance, result

    def prune_stale_records(self, initial_ids, synced_ids):
        """
        Delete records that existed when sync started but were
        not seen as we iterated through all records from REST API.
        """
        stale_ids = initial_ids - synced_ids
        deleted_count = 0
        if stale_ids:
            delete_qset = self.get_delete_qset(stale_ids)
            deleted_count = delete_qset.count()

            pre_delete_result = None
            logger.info(
                'Removing {} stale records for model: {}'.format(
                    len(stale_ids), self.model_class.__bases__[0].__name__,
                )
            )
            delete_qset.delete()

        return deleted_count

    def get_delete_qset(self, stale_ids):
        return self.model_class.objects.filter(pk__in=stale_ids)


class TicketSynchronizer(Synchronizer):
    endpoint = 'Tickets'
    response_key = endpoint.lower()
    model_class = models.Ticket

    params = {
        'open_only': True,
    }

    related_meta = {
        'client_id': (models.Client, 'client'),
        'status_id': (models.Status, 'status'),
        'priority_id': (models.Priority, 'priority'),
        'agent_id': (models.Agent, 'agent'),
    }

    def _assign_field_data(self, instance, json_data):
        # summary
        # details
        # last_action_date
        # last_update
        # target_date
        # target_time

        instance.id = json_data.get('id')
        instance.summary = json_data.get('summary')
        instance.details = json_data.get('details')
        instance.last_action_date = parse(json_data.get('lastactiondate'))
        instance.last_update = parse(json_data.get('last_update'))
        instance.target_date = parse(json_data.get('targetdate'))
        instance.target_time = parse(json_data.get('targettime'))

        self.set_relations(instance, json_data)


class StatusSynchronizer(Synchronizer):
    endpoint = 'Status'
    response_key = None
    model_class = models.Status
    params = {}

    def _unpack_records(self, response):
        records = response.json()
        return records

    def _assign_field_data(self, instance, json_data):

        instance.id = json_data.get('id')
        instance.name = json_data.get('name')
        instance.colour = json_data.get('colour')


class PrioritySynchronizer(Synchronizer):
    endpoint = 'Priority'
    response_key = None
    model_class = models.Priority
    params = {}
    lookup_key = 'priorityid'

    def _unpack_records(self, response):
        records = response.json()
        return records

    def _assign_field_data(self, instance, json_data):

        instance.id = json_data.get('priorityid')
        instance.name = json_data.get('name')
        instance.colour = json_data.get('colour')
        instance.is_hidden = json_data.get('ishidden')


class ClientSynchronizer(Synchronizer):
    endpoint = 'Client'
    response_key = 'clients'
    model_class = models.Client
    params = {
        'includeactive': True,
    }

    def _assign_field_data(self, instance, json_data):

        instance.id = json_data.get('id')
        instance.name = json_data.get('name')
        instance.inactive = json_data.get('inactive')


class AgentSynchronizer(Synchronizer):
    endpoint = 'Agent'
    response_key = None
    model_class = models.Agent
    params = {
        'includeactive': True,
    }

    def _unpack_records(self, response):
        records = response.json()
        return records

    def _assign_field_data(self, instance, json_data):

        instance.id = json_data.get('id')
        instance.name = json_data.get('name')
        instance.is_disabled = json_data.get('isdisabled')
        instance.email = json_data.get('email')
        instance.initials = json_data.get('initials')
        instance.firstname = json_data.get('firstname')
        instance.surname = json_data.get('surname')
        instance.colour = json_data.get('colour')
