"""
Provides PSA-specific functions and configurations for the api and sync apps.
If you are adding something that is provided in only ONE place, it shouldn't
be here.

For example, the PSA specific request decorator is only used in the api app,
so it should be in api.py.
"""

from djpsa.halo.records import sync

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
