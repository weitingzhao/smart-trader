import requests
from logics.logic import Logic
from apps.common.models import *
from django.http import JsonResponse
from apps.notifications.signals import notify
from django.shortcuts import render
from rest_framework.authtoken.models import Token
from django.conf import settings  as django_settings

# Create your views here.
instance = Logic()

# Pages -> Accounts

def get_market_summary():
    queries = [
        "SELECT COUNT(*) FROM market_stock_hist_bars_min_ts",
        "SELECT COUNT(*) FROM market_stock_hist_bars_day_ts",
        "SELECT COUNT(*) FROM market_symbol",
        "SELECT COUNT(*) FROM market_stock",
        "SELECT COUNT(*) FROM market_company_officer",
        "SELECT COUNT(*) FROM market_stock_dividend",
        "SELECT COUNT(*) FROM market_stock_financial",
        "SELECT COUNT(*) FROM market_stock_performance",
        "SELECT COUNT(*) FROM market_stock_price",
        "SELECT COUNT(*) FROM market_stock_risk_metrics",
        "SELECT COUNT(*) FROM market_stock_share",
        "SELECT COUNT(*) FROM market_stock_target",
        "SELECT COUNT(*) FROM market_stock_valuation"
    ]

    counts = {}
    with connection.cursor() as cursor:
        for query in queries:
            cursor.execute(query)
            table_name = query.split(" ")[3]
            counts[table_name] = cursor.fetchone()[0]
    return counts


def settings(request):
    return render(
        request,
        template_name='pages/settings/admin_panel/settings.html',
        context = {
            'parent': 'tools',
            'segment': 'settings',
            'counts': get_market_summary()
        })

def my_handler(sender, instance, created, **kwargs):
    notify.send(instance, verb='was saved')




def lookup(request):
    if request.method == 'GET':
        lookups = UtilitiesLookup.objects.all().values('category', 'type', 'key', 'value')
        return JsonResponse(list(lookups), safe=False)



def lookup_page(request):
    # Ensure the user has a token
    token, created = Token.objects.get_or_create(user=request.user)

    categories = []
    if token:
        api_url = f'{django_settings.API_BASE_URL}/api/lookup'
        response = requests.get(api_url, headers={'Authorization': f'Token {token.key}'})
        if response.status_code == 200:
            categories = response.json()


    return render(
        request,
        template_name='pages/settings/admin_panel/lookup.html',
        context={
            'parent': 'tools',
            'segment': 'lookup',
            'categories': categories,
        })

def get_lookup_types_by_category(reqeust):
    category = reqeust.GET.get('category')
    types = UtilitiesLookup.objects.filter(category=category).values_list('type', flat=True).distinct()
    return JsonResponse({'types': list(types)})