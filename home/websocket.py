from django.urls import re_path
from home.web_sockets.stock_price_ws import StockPriceWS

websocket_urlpatterns = [
    re_path(r'ws/stock_prices/$', StockPriceWS.as_asgi()),
]