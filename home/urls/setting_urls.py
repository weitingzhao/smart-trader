from home import views
from django.urls import path

#all below path with admin/setting/...
urlpatterns = [

    # Tools -> Settings
    path('', views.setting.settings, name="settings"),


    # Tools -> Customize
    path('customize/', views.setting.customize, name='customize'),
    path('customize/position_sizing', views.setting.customize_position_sizing, name='customize_position_sizing'),

    # Tools -> Lookup
    path('lookup/', views.setting.lookup_page, name='lookup_api'),

    # Tools -> Celery Task
    path('celery_task/<str:task_name>/<str:args>', views.setting.celery_task, name="celery_task"),
]
