from django.urls import include, path
from home import views

urlpatterns = [

    ########## Default Index ####################
    path('', views.main.index, name='index'),

    ########## Main System ####################

    # 1. Dashboard
    # path('dashboard/', include('home.urls.dashboard_urls')),
    # # 2. Screening
    path('screening/', include('home.urls.screening_urls')),
    # # 3. Wishlist
    # path('wishlist/', include('home.urls.wishlist_urls')),
    # # 4. Position
    path('position/', include('home.urls.position_urls')),
    # # 5. Performance
    # path('performance/', include('home.urls.performance_urls')),
    # # 6. Cash Flow
    # path('cashflow/', include('home.urls.cash_flow_urls')),
    # # 7. Report & Analytics
    # path('analytics/', include('home.urls.analytics_urls')),
    # # 8. Settings
    path('settings/', include('home.urls.settings_urls')),


    ########## Utilities ############$$########

    # Auto Reminder & Task Logs
    path('auto_reminder/', views.main.auto_reminder, name='auto_reminder'),
    path('tasks_logs/', views.main.get_task_log, name='get_task_log'),
    # Authorization & Authentication
    path('accounts/', include('home.urls.accounts_urls')),
    path('logout/', views.account.logout_view, name='logout'),
    # Error
    path('error/404/', views.accounts.error_404, name="error_404"),
    path('error/500/', views.accounts.error_500, name="error_500"),
]
