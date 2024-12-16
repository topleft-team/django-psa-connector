"""
Provides PSA-specific functions and configurations for the api and sync apps.
If you are adding something that is provided in only ONE place, it shouldn't
be here.

For example, the PSA specific request decorator is only used in the api app,
so it should be in api.py.
"""
from collections import OrderedDict

from djpsa.halo.records import sync
from django.utils.translation import gettext_lazy as _


def critical_priority_sync():
    return OrderedDict([
            ('user', (sync.HaloUserSynchronizer, _('User'))),
            ('agent', (sync.AgentSynchronizer, _('Agent'))),
            ('client', (sync.ClientSynchronizer, _('Client'))),
            ('ticket', (sync.TicketSynchronizer, _('Ticket'))),
            ('appointment', (sync.AppointmentSynchronizer, _('Appointment'))),
            ('action', (sync.ActionSynchronizer, _('Action'))),
        ])


def high_priority_sync():
    return OrderedDict([
        ('status', (sync.StatusSynchronizer, _('Status'))),
        ('priority', (sync.PrioritySynchronizer, _('Priority'))),
        ('team', (sync.TeamSynchronizer, _('Team'))),
        ('user', (sync.HaloUserSynchronizer, _('User'))),
        ('agent', (sync.AgentSynchronizer, _('Agent'))),
        ('client', (sync.ClientSynchronizer, _('Client'))),
        ('ticket', (sync.TicketSynchronizer, _('Ticket'))),
        ('appointment', (sync.AppointmentSynchronizer, _('Appointment'))),
        ('action', (sync.ActionSynchronizer, _('Action'))),
    ])


def medium_priority_sync():
    return OrderedDict([
        ('sla', (sync.SLASynchronizer, _('SLA'))),
        ('site', (sync.SiteSynchronizer, _('Site'))),
        ('ticket_type', (sync.TicketTypeSynchronizer, _('TicketType'))),
    ])


def low_priority_sync():
    return OrderedDict([
    ])
