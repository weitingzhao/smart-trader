from django.core.paginator import Paginator
from logic.logic import Logic
from django.shortcuts import render

from home.models import MarketStockHistoricalBarsByMin

# Create your views here.
instance = Logic()

def stock_screener(request):
    query = request.GET.get('q')
    if query:
        market_data = MarketStockHistoricalBarsByMin.objects.filter(symbol__icontains=query)
    else:
        market_data = MarketStockHistoricalBarsByMin.objects.all()

    paginator = Paginator(market_data, 10)  # Show 10 items per page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Format the time field to display only the date
    for item in page_obj:
        item.time = item.time.strftime('%Y-%m-%d')

    status_message = request.GET.get('status_message', '')

    return render(
        request=request,
        template_name='pages/stock_screener.html',
        context= {
            'parent': 'research',
            'segment': 'stock screener',
            'page_obj': page_obj,
            'status_message': status_message}
    )