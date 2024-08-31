import os
from datetime import datetime, timedelta

import pandas as pd
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from pandas.core.indexes import interval

from home.models import MarketStock, MarketSymbol
from home.models.market import MarketStockHistoricalBarsByDay
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

    symbol = MarketSymbol.objects.select_related(
        "stock"
    ).get(symbol=symbol)

    if symbol is None:
        return render(request, 'accounts/error/404.html')

    stock = symbol.stock

    context = {
        'parent': 'pages',
        'sub_parent': 'stock',
        'segment': 'stock_quote',
        'symbol': symbol.symbol,
        "stock": {
            'symbol': {
                "name": symbol.name.upper(),
                "market": symbol.market,
            },
            "stock":{
                "short_name":stock.short_name,
                "long_name":stock.long_name,
                "sector":stock.sector,
                "industry":stock.industry,
                "long_business_summary":stock.long_business_summary,
            }
        }
    }
    return render(request, 'pages/stock/quote.html', context)

def get_stock_data(request):
    global cutoff_date
    symbol = request.GET.get('symbol')
    interval = request.GET.get('interval', 'daily')

    stock_data = MarketStockHistoricalBarsByDay.objects.filter(symbol=symbol).values('time', 'open', 'high', 'low', 'close', 'volume')
    df = pd.DataFrame(list(stock_data))
    df['time'] = pd.to_datetime(df['time'], utc=True)  # Ensure 'time' column is datetime with UTC

    if interval == 'daily':
        cutoff_date = datetime.now(tz=pd.Timestamp.now().tz) - timedelta(days=16*30)  # Approx 16 months
    elif interval == 'weekly':
        cutoff_date = datetime.now(tz=pd.Timestamp.now().tz) - timedelta(weeks=7*52)  # 7 years
    elif interval == 'monthly':
        cutoff_date = datetime.now(tz=pd.Timestamp.now().tz) - timedelta(weeks=16*52)  # 16 years

    cutoff_date = pd.Timestamp(cutoff_date, tz='UTC')  # Ensure cutoff_date is datetime with UTC

    # Calculate 50-day and 200-day SMA
    df['SMA_50'] = df['close'].rolling(window=50).mean()
    df['SMA_200'] = df['close'].rolling(window=200).mean()

    df = df[df['time'] >= cutoff_date]

    if interval == 'weekly':
        df.set_index('time', inplace=True)
        df = df.resample('W').agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum',
            'SMA_50': 'last',
            'SMA_200': 'last'
        }).dropna().reset_index()
    elif interval == 'monthly':
        df.set_index('time', inplace=True)
        df = df.resample('M').agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum',
            'SMA_50': 'last',
            'SMA_200': 'last'
        }).dropna().reset_index()


    data = {
        'time': df['time'].tolist(),
        'open': df['open'].tolist(),
        'high': df['high'].tolist(),
        'low': df['low'].tolist(),
        'close': df['close'].tolist(),
        'volume': df['volume'].tolist(),
        'SMA_50': df['SMA_50'].tolist(),
        'SMA_200': df['SMA_200'].tolist()
    }

    return JsonResponse(data)

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