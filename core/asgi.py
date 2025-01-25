"""
ASGI config for core project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""
import django
import os
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import threading
import ray
from django.apps import apps
import home.websocket as home_websocket

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# init ray
# ray.init() # no need add ray now

bokeh_app_config = apps.get_app_config('bokeh_django')

application = ProtocolTypeRouter({
    'http': AuthMiddlewareStack(
        URLRouter(
            bokeh_app_config.routes.get_http_urlpatterns()
        )
    ),
    'websocket': AuthMiddlewareStack(
        URLRouter(
            bokeh_app_config.routes.get_websocket_urlpatterns() +
            home_websocket.websocket_urlpatterns
        )
    ),
})

# Ensure signal handling is only set up in the main thread
if threading.current_thread() == threading.main_thread():
    from .shutdown import handle_shutdown
    handle_shutdown()
