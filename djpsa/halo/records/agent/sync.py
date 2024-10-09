from djpsa.halo.records import models
from djpsa.halo.records import api
from djpsa.sync.sync import Synchronizer


class AgentSynchronizer(Synchronizer):
    model_class = models.AgentTracker
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

