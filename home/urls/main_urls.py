from home import views
from django.urls import path

#all below path with /...
urlpatterns = [

    # Menu: Dashboard
    path('', views.play_ground.index, name='index'),

    # Navigation:  Auto Reminder
    path('auto_reminder/', views.main.auto_reminder, name='auto_reminder'),

    # Menu: Research
    path('stock_screener/', views.research.stock_screener, name='stock screener'),
    path('stock/quote/<str:symbol>', views.main.stock_quote, name="stock_quote"),


    # Test Phase 2.
    path('billing/', views.play_ground.billing, name='billing'),
    path('tables/', views.play_ground.tables, name='tables'),
    path('profile/', views.play_ground.profile, name='profile'),
    # path("<int:question_id>/", views.detail, name="detail"),
    # path("<int:question_id>/results/", views.results, name="results"),
    # path("<int:question_id>/vote/", views.vote, name="vote"),
]
