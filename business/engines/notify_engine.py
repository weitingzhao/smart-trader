from typing import Union
from django.db import models
from datetime import timedelta

from django.http import JsonResponse
from django.utils import timezone
from core.configures_home import Config
from apps.notifications.signals import notify
from .base_engine import BaseEngine
from django.contrib.auth.models import AnonymousUser

from enum import Enum

class Level(Enum):
    SUCCESS = 'success'
    INFO = 'info'
    WARNING = 'warning'
    ERROR = 'error'

class NotifyEngine(BaseEngine):

    def __init__(self, config: Config, sender: AnonymousUser):
        super().__init__(config)
        self.sender = sender


    def send(self,
             # Required
             recipient : AnonymousUser,
             verb: str,
             # Optional
             level: Union[Level, str] = Level.INFO,
             description: str = None,
             action_object : models.Model = None,
             target: models.Model = None,
             public: bool =True,
             data: object = None) -> JsonResponse:
        if isinstance(level, str):
            level = Level(level)
        elif not isinstance(level, Level):
            return JsonResponse({'success': False, 'error': "Invalid notification level"})
        try:
            array = notify.send(
                # Required
                sender=self.sender,
                recipient=recipient,
                verb=verb,
                #optional
                level=level.value,
                description=description,
                action_object=action_object,
                target=target,
                public=public,
                data=data,
                timestamp=timezone.now() - timedelta(hours=15)
            )
            # Extract notifications from the array
            notifications = [notification for handler, notification_list in array for notification in notification_list]
            # Serialize notifications
            serialized_notifications = [str(notification) for notification in notifications]

            return JsonResponse({'success': True, 'data': serialized_notifications})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
