''' Django notifications admin file '''
# -*- coding: utf-8 -*-
from django.contrib import admin
from apps.notifications.base.admin import AbstractNotificationAdmin
from swapper import load_model

try:
    from django.utils.translation import ugettext_lazy as _
except ImportError:
    from django.utils.translation import gettext_lazy as _  # Django 4.0.0 and more


Notification = load_model('notifications', 'Notification')


def mark_unread(modeladmin, request, queryset):
    queryset.update(unread=True)
mark_unread.short_description = _('Mark selected notifications as unread')


class NotificationAdmin(AbstractNotificationAdmin):
    raw_id_fields = ('recipient',)
    readonly_fields = ('action_object_url', 'actor_object_url', 'target_object_url')
    list_display = ('recipient', 'actor',
                    'level', 'target', 'unread', 'public')
    list_filter = ('level', 'unread', 'public', 'timestamp',)
    actions = [mark_unread]

    def get_queryset(self, request):
        qs = super(NotificationAdmin, self).get_queryset(request)
        return qs.prefetch_related('actor')


admin.site.register(Notification, NotificationAdmin)
