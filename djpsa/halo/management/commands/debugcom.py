from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'debug'

    def handle(self, *args, **options):
        print("############")
        print("############")
        print(settings.A_SETTING)
        print("############")
        print("############")
