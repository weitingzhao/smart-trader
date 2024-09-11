from django.urls import include, path
from home import views

urlpatterns = [

    ########## Common ####################
    # Common features
    path('', views.main.index, name='index'),
    # Auto Reminder & Task Logs
    path('auto_reminder/', views.main.auto_reminder, name='auto_reminder'),
    path('tasks_logs/', views.main.get_task_log, name='get_task_log'),


    ########## Component ####################
    # Component 1. Research
    path('research/', include('home.urls.research_urls')),

    # Component 2. Portfolio
    path('portfolio/', include('home.urls.portfolio_urls')),

    # Component 3. Tools
    path('tools/', include('home.urls.tools_urls')),


    ########## Utilities ############$$########
    # Utilities X : Authentication & Error
    path('error/404/', views.accounts.error_404, name="error_404"),
    path('error/500/', views.accounts.error_500, name="error_500"),
    path('accounts/', include('home.urls.accounts_urls')),
    path('logout/', views.account.logout_view, name='logout'),
]
