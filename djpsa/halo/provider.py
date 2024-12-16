"""
Provides PSA-specific functions and configurations for the api and sync apps.
If you are adding something that is provided in only ONE place, it shouldn't
be here.

For example, the PSA specific request decorator is only used in the api app,
so it should be in api.py.
"""

from djpsa.halo.records import sync


def critical_priority_sync():
    return [
            sync.HaloUserSynchronizer,
            sync.AgentSynchronizer,
            sync.ClientSynchronizer,
            sync.TicketSynchronizer,
            sync.AppointmentSynchronizer,
            sync.ActionSynchronizer,
        ]


def high_priority_sync():
    return [
        sync.StatusSynchronizer,
        sync.PrioritySynchronizer,
        sync.TeamSynchronizer,
        sync.HaloUserSynchronizer,
        sync.AgentSynchronizer,
        sync.ClientSynchronizer,
        sync.TicketSynchronizer,
        sync.AppointmentSynchronizer,
        sync.ActionSynchronizer,
    ]


def medium_priority_sync():
    return [
        sync.SLASynchronizer,
        sync.SiteSynchronizer,
        sync.TicketTypeSynchronizer,
    ]


def low_priority_sync():
    return []
