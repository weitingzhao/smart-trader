from django.urls import re_path
from home.services.price_monitor_ws import StockMonitorWS

websocket_urlpatterns = [
    re_path(r'ws/stock_quote/$', StockMonitorWS.as_asgi()),
]