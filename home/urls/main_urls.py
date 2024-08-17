from home import views
from django.urls import path


urlpatterns = [

    # Navigation -> auto reminder
    path('auto_reminder/', views.main.auto_reminder, name='auto_reminder'),

    # Pages -> Profile
    path('stock/quote/<str:symbol>', views.main.stock_quote, name="stock_quote"),


    # Test Phase 1. Second Stock Screener
    path('stock_screener/', views.play_ground.stock_screener, name='stock screener'),
    path('refresh_market_symbol/', views.play_ground.refresh_market_symbol, name='refresh_market_symbol'),
    path('refresh_market_stock/', views.play_ground.refresh_market_stock, name='refresh_market_stock'),
    path('index_market_symbol/', views.play_ground.index_market_symbol, name='index_market_symbol'),
    path('refresh_company_overview/', views.play_ground.refresh_company_overview, name='refresh_company_overview'),
    # Dashboard
    path('', views.play_ground.index, name='index'),

    # Test Phase 2.
    path('billing/', views.play_ground.billing, name='billing'),
    path('tables/', views.play_ground.tables, name='tables'),
    path('profile/', views.play_ground.profile, name='profile'),
    # path("<int:question_id>/", views.detail, name="detail"),
    # path("<int:question_id>/results/", views.results, name="results"),
    # path("<int:question_id>/vote/", views.vote, name="vote"),
]
