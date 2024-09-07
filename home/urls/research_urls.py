from home import views
from django.urls import path

#all below path with /...
urlpatterns = [




    # Menu: Research
    path('stock/screener/', views.research.stock_screener, name='stock_screener'),

    path('stock/quote/<str:symbol>', views.research.stock_quote, name="stock_quote"),

    path('api/stock_data', views.research.get_stock_data, name='get_stock_data'),
]
