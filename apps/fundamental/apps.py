from django.apps import AppConfig
from apps.fundamental.instance import Instance


class CommonConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.fundamental'

    def ready(self):
        Instance()