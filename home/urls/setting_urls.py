from home import views
from django.urls import path

#all below path with admin/setting/...
urlpatterns = [

    # Dashboard -> Settings
    path('', views.setting.settings, name="settings"),

    # Dashboard -> Settings -> Data -> Fundamentals
    path('celery_task/<str:task_name>', views.setting.celery_task, name="celery_task"),
]
