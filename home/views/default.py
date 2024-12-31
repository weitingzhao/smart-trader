import os
from django.conf import settings
from django.http import JsonResponse, HttpResponse
import business.logic as Logic
from django.shortcuts import render
from django.views.decorators.http import require_GET


def index(request):
    context = {
        'parent': 'home',
        'segment': 'index',
    }
    return render(request, template_name='pages/index.html', context= context)

# i18n
def i18n_view(request):
  context = {
    'parent': 'apps',
    'segment': 'i18n'
  }
  return render(request, 'pages/apps/i18n.html', context)


@require_GET
def auto_reminder(request):
    query = request.GET.get('query', '')
    return JsonResponse(Logic.service().loading().symbol().match_symbol(query, 20), safe=False)

@require_GET
def get_task_log(request):
    file_name = request.GET.get('file')
    full_path = os.path.join(settings.CELERY_LOGS_DIR, f"{file_name}.log")
    try:
        with open(full_path, 'r') as file:
            content = file.read()
        return HttpResponse(content, content_type='text/plain')
    except FileNotFoundError:
        return HttpResponse('File not found', status=404)