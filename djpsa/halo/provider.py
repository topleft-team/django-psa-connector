"""
Provides PSA-specific functions and configurations for the api and sync apps.
If you are adding something that is provided in only ONE place, it shouldn't be here.
For example, the PSA specific request decorator is only used in the api app,
so it should be in api.py.
"""

from django.conf import settings

from djpsa.halo import sync

f = {s.model_class: s for s in [
    sync.TicketSynchronizer,
    sync.StatusSynchronizer,
    sync.PrioritySynchronizer,
    sync.AgentSynchronizer,
    sync.ClientSynchronizer,
]}


def sync_factory(model_class):
    return f[model_class]


def get_auth():
    pass


def get_request_settings():
    # Make some defaults
    request_settings = {
        'timeout': 30.0,
        'batch_size': 100,
        'max_attempts': 3,
    }

    if hasattr(settings, 'HALO_CONF_CALLABLE'):
        request_settings.update(settings.HALO_CONF_CALLABLE())

    return request_settings
