from django.apps import AppConfig
from django.conf import settings


class HaloConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'djpsa.halo'


    def ready(self):
        from djpsa.halo import provider
        # TODO friday rename PSA_MODULE to something better
        settings.PSA_MODULE = provider
