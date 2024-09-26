import requests
from logic.logic import Logic
from apps.common.models import *
from django.contrib import messages
from django.http import JsonResponse
from apps.notifications.signals import notify
from django.shortcuts import render, redirect
from rest_framework.authtoken.models import Token
from django.conf import settings  as django_settings
from home.forms.portfolio import PositionSizingForm

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
        template_name='pages/tools/settings.html',
        context = {
            'parent': 'tools',
            'segment': 'settings',
            'counts': get_market_summary()
        })

def my_handler(sender, instance, created, **kwargs):
    notify.send(instance, verb='was saved')

def customize(request):
    try:
        position_sizing = PositionSizing.objects.get(user=request.user)
        form = PositionSizingForm(instance=position_sizing)
    except PositionSizing.DoesNotExist:
        form = PositionSizingForm()

    return render(
        request,
        template_name='pages/tools/customize.html',
        context = {
            'parent': 'account',
            'segment': 'customize',
            'position_sizing_form': form,
            'messages': messages.get_messages(request),
        })

def customize_position_sizing(request):
    if request.method == 'POST':
        form = PositionSizingForm(request.POST)
        if form.is_valid():
            position_sizing, created = PositionSizing.objects.update_or_create(
                user=request.user,
                defaults=form.cleaned_data
            )
            if created:
                messages.success(request, 'Position Sizing created successfully.', extra_tags='position sizing')
            else:
                messages.success(request, 'Position Sizing updated successfully.', extra_tags='position sizing')
        else:
            messages.error(request, f'Position Sizing form is invalid.', extra_tags='position sizing')
            return render(
                request,
                template_name='pages/tools/customize.html',
                context={
                    'parent': 'account',
                    'segment': 'customize',
                    'position_sizing_form': form,
                })
    else:
        messages.error(request, "method not supported", extra_tags='position sizing')

    return redirect('customize')

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
        template_name='pages/tools/lookup.html',
        context={
            'parent': 'tools',
            'segment': 'lookup',
            'categories': categories,
        })

def get_lookup_types_by_category(reqeust):
    category = reqeust.GET.get('category')
    types = UtilitiesLookup.objects.filter(category=category).values_list('type', flat=True).distinct()
    return JsonResponse({'types': list(types)})