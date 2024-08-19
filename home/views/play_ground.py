from django.urls import reverse
from home.base_home import BaseHome
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from home.models import MarketStockHistoricalBars

# Create your views here.
instance = BaseHome()

# Pages
def index(request):
    return render(request, 'pages/index.html', {'segment': 'index'})

def refresh_market_symbol(request):
    if request.method == 'POST':
        instance.service.fetching().symbol().fetching_symbol()
        return redirect(reverse('stock screener') + '?status_message=All Market Symbol updated successfully')
    return redirect('stock screener')

def refresh_market_stock(request):
    if request.method == 'POST':
        instance.service.fetching().symbol().fetch_symbols_info()
        return redirect(reverse('stock screener') + '?status_message=All Market Stock updated successfully')
    return redirect('stock screener')

def index_market_symbol(request):
    if request.method == "POST":
        instance.service.saving().symbol().index_symbol()
        return redirect(reverse('stock screener') + '?status_message=Market symbols indexed successfully')
    return redirect('stock screener')

def stock_screener(request):
    query = request.GET.get('q')
    if query:
        market_data = MarketStockHistoricalBars.objects.filter(symbol__icontains=query)
    else:
        market_data = MarketStockHistoricalBars.objects.all()

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
            'page_obj': page_obj,
            'segment': 'stock screener',
            'status_message': status_message}
    )


def billing(request):
    return render(request, 'pages/billing.html', {'segment': 'billing'})
def tables(request):
    return render(request, 'pages/tables.html', {'segment': 'tables'})
def profile(request):
    return render(request, 'pages/profile.html', {'segment': 'profile'})




# from .models import Question
# def detail(request, question_id):
#     latest_question_list = Question.objects.order_by("-pub_date")[:5]
#     output = ", ".join([q.question_text for q in latest_question_list])
#     return HttpResponse(output)
# def results(request, question_id):
#     response = "You're looking at the results of question %s."
#     return HttpResponse(response % question_id)
# def vote(request, question_id):
#     return HttpResponse("You're voting on question %s." % question_id)

