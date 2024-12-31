import pandas as pd
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from apps.common.models import *
from django.db.models import F
import json
from business.utilities.dates import Dates


def default(request):
    return render(
        request=request,
        template_name='pages/screening/screening_criteria.html',
        context= {
            'parent': 'screening',
            'segment': 'screening_criteria',
        })


@csrf_exempt
def stock_search(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            selected_options = data.get('selectedOptions', [])
            views_filter = data.get('views-filter', 'Tables')
            views_value = data.get('views-value', 'overview')
            sorted_by = data.get('sortedBy', '')
            desc = data.get('desc', '')
            chart_per_line = data.get('chartPerLine', '')
            page = data.get('page', 1)  # Get the page number from the request, default to 1

            # Initialize the queryset
            queryset = MarketSymbol.objects.filter(is_delisted=False).annotate(
                market_cap=F('stock_valuation__market_cap')
            )

            print("page"+str(page))


            # Apply filters based on selected_options
            for option in selected_options:
                source = option.get('source')
                key = option.get('key')

                if source and key:
                    if source == "dropdown_General_Exchange":
                        queryset = queryset.filter(market__exact=key)
                    else:
                        queryset = queryset.filter(**{source: key})

            # Get the total count of the filtered queryset
            total_count = queryset.count()

            if views_filter == 'Charts':
                # Construct the URL for the chart image
                chart_data = []
                for symbol in queryset.values_list('symbol', flat=True):
                    chart_data.append({
                        'symbol': symbol,
                        'period': 'daily',
                        'type': 'Candles-Full',
                        'elements': 80
                    })

                # Paginate the chart URLs
                paginator = Paginator(chart_data, 40)  # Show 20 items per page
                page_obj = paginator.get_page(page)

                return JsonResponse({
                    'results': list(page_obj),
                    'total_count': total_count
                }, safe=False, status=200)
            else:
                # Convert queryset to a list of dictionaries
                queryset_values = queryset.values('symbol', 'name', 'market', 'market_cap')

                # Paginate the results
                paginator = Paginator(queryset_values, 40)  # Show 10 items per page
                page_obj = paginator.get_page(page)

                return JsonResponse({
                    'results': list(page_obj),
                    'total_count': total_count
                }, safe=False, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)


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
        template_name='pages/screening/stock_screener.html',
        context= {
            'parent': 'research',
            'segment': 'stock screener',
            'page_obj': page_obj,
            'status_message': status_message}
    )


def get_stock_data(request):
    symbol = request.GET.get('symbol')
    interval = request.GET.get('interval', 'daily')

    stock_data = MarketStockHistoricalBarsByDay.objects.filter(symbol=symbol).values('time', 'open', 'high', 'low', 'close', 'volume')
    df = pd.DataFrame(list(stock_data))
    df['time'] = pd.to_datetime(df['time'], utc=True)  # Ensure 'time' column is datetime with UTC

    cutoff_date = Dates.cutoff_date(interval)

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

def stock_charts(request):
    return render(
        request=request,
        template_name='pages/screening/stock_charts.html',
        context= {
            'parent': 'research',
            'segment': 'stock charts',
        })



