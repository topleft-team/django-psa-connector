from django.apps import AppConfig


class HaloConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'djpsa.halo'
    label = 'halo'

    def ready(self):
        pass
