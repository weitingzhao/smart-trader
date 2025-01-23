from django.urls import include, path
from home import views

urlpatterns = [

    ########## Default Index ####################
    # Default Index
    path('', views.main.index, name='index'),
    # Auto Reminder & Task Logs
    path('auto_reminder/', views.main.auto_reminder, name='auto_reminder'),
    path('tasks_logs/', views.main.get_task_log, name='get_task_log'),



    ########## Main System ####################
    # 1. Dashboard
    path('dashboard/', include('home.urls.dashboard')),
    # # 2. Screening
    path('screening/', include('home.urls.screening')),
    # # 3. Position
    path('position/', include('home.urls.position')),
    # # 4. Performance
    path('performance/', include('home.urls.performance')),
    # # 5. Cash Flow
    path('cashflow/', include('home.urls.cash_flow')),
    # # 6. Report & Analytics
    path('analytics/', include('home.urls.analytics')),
    # # 7. Settings
    path('settings/', include('home.urls.settings')),

    # # 0. Transaction
    path('transaction/', include('home.urls.transaction')),

    ########## Utilities ############$$########
    # Authorization & Authentication
    path('accounts/', include('home.urls.accounts')),
    path('logout/', views.account.logout_view, name='logout'),
    # Error
    path('error/404/', views.accounts.error_404, name="error_404"),
    path('error/500/', views.accounts.error_500, name="error_500"),
]
