''' Django notifications apps file '''
# -*- coding: utf-8 -*-
from django.apps import AppConfig
try:
    from django.utils.translation import ugettext_lazy as _
except ImportError:
    from django.utils.translation import gettext_lazy as _  # Django 4.0.0 and more


class Config(AppConfig):
    name = "apps.notifications"
    verbose_name = _("Notifications")
    default_auto_field = 'django.db.models.AutoField'

    def ready(self):
        super(Config, self).ready()
        # this is for backwards compatibility
        import apps.notifications.signals
        apps.notifications.notify = apps.notifications.signals.notify
