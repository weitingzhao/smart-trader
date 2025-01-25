from django.urls import re_path
from home.services.price_quote_ws import StockPriceWS

websocket_urlpatterns = [
    re_path(r'ws/stock_prices/$', StockPriceWS.as_asgi()),
]