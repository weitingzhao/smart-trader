"""
ASGI config for core project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.apps import apps

# from django.core.asgi import get_asgi_application
# application = get_asgi_application()
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')


bokeh_app_config = apps.get_app_config('bokeh_django')

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(URLRouter(bokeh_app_config.routes.get_websocket_urlpatterns())),
    'http': AuthMiddlewareStack(URLRouter(bokeh_app_config.routes.get_http_urlpatterns())),
})

