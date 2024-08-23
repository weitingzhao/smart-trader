import os

from django.conf import settings
from django.http import JsonResponse, HttpResponse
from logic.logic import Logic
from django.shortcuts import render
from django.views.decorators.http import require_GET


# Create your views here.
instance = Logic()

@require_GET
def auto_reminder(request):
    query = request.GET.get('query', '')
    return JsonResponse(instance.service.loading().symbol().match_symbol(query, 20), safe=False)

def stock_quote(request, symbol):
  context = {
    'parent': 'pages',
    'sub_parent': 'stock',
    'segment': 'stock_quote',
    'symbol': symbol
  }
  return render(request, 'pages/stock/quote.html', context)

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