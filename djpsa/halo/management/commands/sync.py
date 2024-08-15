from django.core.management.base import BaseCommand
from djpsa.sync.sync import TicketSynchronizer, StatusSynchronizer, \
    PrioritySynchronizer, ClientSynchronizer, AgentSynchronizer

OPTION_NAME = 'sync_object'


class Command(BaseCommand):
    help = 'Synchronize'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument(OPTION_NAME, nargs='?', type=str)
        parser.add_argument('--full',
                            action='store_true',
                            dest='full',
                            default=False)

    def handle(self, *args, **options):
        sync_classes = []
        object_arg = options[OPTION_NAME]
        full_option = options.get('full', False)

        StatusSynchronizer().sync()
        PrioritySynchronizer().sync()
        ClientSynchronizer().sync()
        AgentSynchronizer().sync()
        TicketSynchronizer().sync()

