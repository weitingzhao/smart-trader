from apps.notifications.apps import Config as NotificationConfig


class SampleNotificationsConfig(NotificationConfig):
    name = 'apps.notifications.tests.sample_notifications'
    label = 'sample_notifications'
