from django.urls import re_path
from home.services.price_quote_ws import StockQuoteWS

websocket_urlpatterns = [
    re_path(r'ws/stock_quote/$', StockQuoteWS.as_asgi()),
]