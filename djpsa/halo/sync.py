from django.core.exceptions import ObjectDoesNotExist
from dateutil.parser import parse

from djpsa.halo import models
from djpsa.halo import api
from djpsa.sync.sync import Synchronizer


# README #
#
# "response_key"
#    The Halo API is very inconsistent, the response_key field is used to
#     specify the key in the response that contains the data we want to unpack.
#
#     Where when the response is just a list with no key, the response_key is
#     omitted from the class. ResponseKeyMixin should be applied to any class
#     that requires the response_key field.
#
# "lookup_key"
#    Some records need to be tracked by a different field than id for the
#     primary key. For example, the priority model uses priorityid as the
#     primary key, so the lookup_key is set to 'priorityid'. This is because
#     in the Halo API the 'id' seems to be a large alphanumeric string, and
#     isn't used on the ticket model.


class ResponseKeyMixin:
    response_key = None

    def _unpack_records(self, response):
        records = response[self.response_key]
        return records


class TicketSynchronizer(ResponseKeyMixin, Synchronizer):
    response_key = 'tickets'
    model_class = models.Ticket
    client_class = api.TicketAPI
    last_updated_field = 'lastupdatefromdate'

    related_meta = {
        'client_id': (models.Client, 'client'),
        'status_id': (models.Status, 'status'),
        'priority_id': (models.Priority, 'priority'),
        'agent_id': (models.Agent, 'agent'),
        'sla_id': (models.SLA, 'sla'),
    }

    def __init__(self, full=False, *args, **kwargs):

        if full:
            self.conditions.append({
                'open_only': True,
            })

        super().__init__(full, *args, **kwargs)

    def _assign_field_data(self, instance, json_data):
        instance.id = json_data.get('id')
        instance.summary = json_data.get('summary')
        instance.details = json_data.get('details')
        instance.last_action_date = parse(json_data.get('lastactiondate'))
        instance.last_update = parse(json_data.get('last_update'))
        instance.target_date = parse(json_data.get('targetdate'))
        instance.target_time = parse(json_data.get('targettime'))

        self.set_relations(instance, json_data)


class StatusSynchronizer(Synchronizer):
    model_class = models.Status
    client_class = api.StatusAPI

    def _assign_field_data(self, instance, json_data):

        instance.id = json_data.get('id')
        instance.name = json_data.get('name')
        instance.colour = json_data.get('colour')


class PrioritySynchronizer(Synchronizer):
    model_class = models.Priority
    lookup_key = 'priorityid'
    client_class = api.PriorityAPI

    def _assign_field_data(self, instance, json_data):

        instance.id = json_data.get('priorityid')
        instance.name = json_data.get('name')
        instance.colour = json_data.get('colour')
        instance.is_hidden = json_data.get('ishidden')


class ClientSynchronizer(ResponseKeyMixin, Synchronizer):
    response_key = 'clients'
    model_class = models.Client
    client_class = api.ClientAPI

    def __init__(self, full=False, *args, **kwargs):

        self.conditions.append({
            'includeactive': True,
        })

        super().__init__(full, *args, **kwargs)

    def _assign_field_data(self, instance, json_data):

        instance.id = json_data.get('id')
        instance.name = json_data.get('name')
        instance.inactive = json_data.get('inactive')


class AgentSynchronizer(Synchronizer):
    model_class = models.Agent
    client_class = api.AgentAPI

    def __init__(self, full=False, *args, **kwargs):

        self.conditions.append({
            'includeactive': True,
        })

        super().__init__(full, *args, **kwargs)

    def _assign_field_data(self, instance, json_data):

        instance.id = json_data.get('id')
        instance.name = json_data.get('name')
        instance.is_disabled = json_data.get('isdisabled')
        instance.email = json_data.get('email')
        instance.initials = json_data.get('initials')
        instance.firstname = json_data.get('firstname')
        instance.surname = json_data.get('surname')
        instance.colour = json_data.get('colour')


class SLASynchronizer(Synchronizer):
    model_class = models.SLA
    client_class = api.StatusAPI

    def _assign_field_data(self, instance, json_data):

        instance.id = json_data.get('id')
        instance.name = json_data.get('name')
        instance.hours_are_techs_local_time = json_data.get('hoursaretechslocaltime', False)
        instance.response_reset = json_data.get('responsereset', False)
        instance.response_reset_approval = json_data.get('response_reset_approval', False)
        instance.track_sla_fix_by_time = json_data.get('trackslafixbytime', False)
        instance.track_sla_response_time = json_data.get('trackslaresponsetime', False)
        instance.workday_id = json_data.get('workday_id')
        instance.auto_release_limit = json_data.get('autoreleaselimit')
        instance.auto_release_option = json_data.get('autoreleaseoption', False)
        instance.status_after_first_warning = json_data.get('statusafterfirstwarning')
        instance.status_after_second_warning = json_data.get('statusaftersecondwarning')
        instance.status_after_auto_release = json_data.get('statusafterautorelease')


class SiteSynchronizer(ResponseKeyMixin, Synchronizer):
    model_class = models.Site
    response_key = 'sites'
    client_class = api.SiteAPI

    related_meta = {
        'client_id': (models.Client, 'client'),
        'sla_id': (models.SLA, 'sla'),
    }

    def __init__(self, full=False, *args, **kwargs):

        self.conditions.append({
            'includeaddress': True,
        })

        super().__init__(full, *args, **kwargs)

    def _assign_field_data(self, instance, json_data):

        instance.id = json_data.get('id')
        instance.name = json_data.get('name')
        # api has client_id as decimal, convert to int. It's never
        # actually a decimal. The API docs has it as an int, but for some
        # reason it's being returned as a decimal on Site records.
        if json_data.get('client_id'):
            json_data['client_id'] = int(json_data.get('client_id'))

        # This is the worst thing I have ever seen.
        instance.delivery_address = json_data.get('delivery_address_line1')
        instance.delivery_address += " {}".format(json_data.get('delivery_address_line2'))
        instance.delivery_address += " {}".format(json_data.get('delivery_address_line3'))
        instance.delivery_address += " {}".format(json_data.get('delivery_address_line4'))
        instance.delivery_address += " {}".format(json_data.get('delivery_address_line5'))

        instance.colour = json_data.get('colour')
        instance.active = json_data.get('active', False)
        instance.phone_number = json_data.get('phone_number')
        instance.use = json_data.get('use')

        self.set_relations(instance, json_data)


class HaloUserSynchronizer(ResponseKeyMixin, Synchronizer):
    model_class = models.HaloUser
    response_key = 'users'
    client_class = api.UserAPI

    related_meta = {
        'client_id': (models.Client, 'client'),
        'linked_agent_id': (models.Agent, 'agent'),
    }

    def __init__(self, full=False, *args, **kwargs):

        self.conditions.append({
            'includeactive': True,
        })

        super().__init__(full, *args, **kwargs)

    def _assign_field_data(self, instance, json_data):
        instance.id = json_data.get('id')
        instance.name = json_data.get('name')
        instance.first_name = json_data.get('firstname')
        instance.surname = json_data.get('surname')
        instance.initials = json_data.get('initials')
        instance.email = json_data.get('emailaddress')
        instance.colour = json_data.get('colour')
        instance.active = not json_data.get('inactive', True)
        instance.login = json_data.get('login')
        instance.use = json_data.get('use')
        instance.never_send_emails = json_data.get('neversendemails', False)
        instance.phone_number = json_data.get('phonenumber')
        instance.mobile_number = json_data.get('mobilenumber')
        instance.mobile_number_2 = json_data.get('mobilenumber2')
        instance.home_number = json_data.get('homenumber')
        instance.tel_pref = json_data.get('telpref')
        instance.is_service_account = json_data.get('isserviceaccount', False)
        instance.is_important_contact = json_data.get('isimportantcontact', False)
        instance.is_important_contact_2 = json_data.get('isimportantcontact2', False)

        if json_data.get('linked_agent_id') == 0:
            json_data['linked_agent_id'] = None

        self.set_relations(instance, json_data)
