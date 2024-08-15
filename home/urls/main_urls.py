from home import views
from django.urls import path


urlpatterns = [

    # Dashboard
    path('', views.main.index, name='index'),

    # other url patterns
    path('auto_reminder/', views.main.auto_reminder, name='auto_reminder'),

    # Stock Screener
    path('stock_screener/', views.main.stock_screener, name='stock screener'),
    path('refresh_market_symbol/', views.mains.refresh_market_symbol, name='refresh_market_symbol'),
    path('index_market_symbol/', views.mains.index_market_symbol, name='index_market_symbol'),

    path('billing/', views.main.billing, name='billing'),
    path('tables/', views.main.tables, name='tables'),
    path('profile/', views.main.profile, name='profile'),

    # path("<int:question_id>/", views.detail, name="detail"),
    # path("<int:question_id>/results/", views.results, name="results"),
    # path("<int:question_id>/vote/", views.vote, name="vote"),
]
