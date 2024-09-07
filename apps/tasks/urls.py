from django.urls import path
from django.views.decorators.http import require_POST

from apps.tasks import views

urlpatterns = [
    # Celery
    path('', views.tasks, name="tasks"),
    path('tasks/run/<str:task_name>'  , views.run_task,    name="run-task"),
    path('tasks/cancel/<str:task_id>' , views.cancel_task, name="cancel-task"),
    path('tasks/retry/<str:task_id>', views.retry_task, name='retry-task'),
    path('tasks/output/'              , views.task_output, name="task-output"),
    path('tasks/log/'                 , views.task_log,    name="task-log"),
    path('download-log-file/<str:file_path>/', views.download_log_file, name='download_log_file'),
]