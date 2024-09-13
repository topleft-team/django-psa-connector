from django.conf import settings

from djpsa.halo import sync
from djpsa.halo import formatter

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


def get_request_formatter():
    return formatter.Formatter()
