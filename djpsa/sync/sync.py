import logging

from django.utils import timezone
from django.db import transaction, IntegrityError
from django.conf import settings

from djpsa.sync.models import SyncJob


logger = logging.getLogger(__name__)

CREATED = 1
UPDATED = 2
SKIPPED = 3


def get_synchronizer(model_class, **kwargs):
    sync_class = settings.PROVIDER.sync_factory(model_class)
    return sync_class(**kwargs)


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


# TODO bug, skipping not happening
class Synchronizer:
    lookup_key = 'id'
    model_class = None
    client_class = None
    last_updated_field = None
    conditions = []

    def __init__(self, full=False, *args, **kwargs):
        request_settings = settings.PROVIDER.get_request_settings()

        self.api_conditions = [condition for condition in self.conditions]
        self.client = self.client_class(self.api_conditions)
        self.partial_sync_support = True
        self.batch_size = request_settings['batch_size']
        self.full = full

    def get_sync_job_qset(self):
        return SyncJob.objects.filter(
            entity_name=self.model_class.__bases__[0].__name__
        )

    @log_sync_job
    def sync(self):

        sync_job_qset = self.get_sync_job_qset().filter(success=True)

        if sync_job_qset.count() > 1 and self.last_updated_field \
                and not self.full and self.partial_sync_support:
            last_sync_job_time = sync_job_qset.last().start_time.strftime(
                '%Y-%m-%dT%H:%M:%S.%fZ')
            self.api_conditions.append({
                self.last_updated_field: last_sync_job_time
            })

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

        page = 1
        while True:
            logger.info(
                'Fetching {} records, batch {}'.format(
                    self.model_class.__bases__[0].__name__, page)
            )
            response = self.client.get_page(page=page)
            records = self._unpack_records(response)
            self.persist_page(records, results)
            page += 1
            if len(records) < self.batch_size:
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
        # TODO left off here, add comment that other synchronizers
        #  can override this method
        return response

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
            elif self._is_instance_changed(instance):
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

    def _is_instance_changed(self, instance):
        return instance.tracker.changed()
