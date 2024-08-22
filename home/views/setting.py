from datetime import datetime
from django.http import JsonResponse
from django.shortcuts import render, redirect
from logic.logic import Logic
from apps.notifications.signals import notify
from apps.tasks import tasks

# Create your views here.
instance = Logic()

# Pages -> Accounts
def settings(request):
    return render(
        request,
        template_name='pages/account/settings.html',
        context = {
            'parent': 'dashboard',
            'segment': 'settings'
        })

def celery_task(request, task_name):
    if request.method != 'GET':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})

    try:
        feedback = tasks.backend_task.delay({
            'user_id': request.user.id,
            'task_name': task_name
        })
        return JsonResponse({
            'success': True,
            'on': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status': feedback.status,
            'task_id': feedback.task_id})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def my_handler(sender, instance, created, **kwargs):
    notify.send(instance, verb='was saved')

