from django.http import JsonResponse
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