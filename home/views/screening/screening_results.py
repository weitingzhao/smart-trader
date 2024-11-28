import talib
import pandas as pd
from apps.common.models import *
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.core.paginator import Paginator

def default(request):

    user_id = request.user.id  # Assuming you have the user_id from the request
    portfolio = Portfolio.objects.filter(user=user_id, is_default=True).order_by('-portfolio_id').first()

    if not portfolio:
        return JsonResponse({'success': False, 'error': 'Default portfolio not found'}, status=404)

    # Part 1. holding_symbols
    symbols = [item.symbol.symbol for item in Holding.objects.filter(portfolio=portfolio)]

    # Loop through each symbol and calculate indicators
    # for symbol in symbols:
    #     calculate_indicators(symbol)


    return render(
        request=request,
        template_name='pages/screening/screening_results.html',
        context= {
            'parent': 'screening',
            'portfolio': portfolio,
            'segment': 'screening_results',
        })

@csrf_exempt
def output(request):
    if request.method == 'POST':
        try:
            user_id = request.user.id  # Assuming you have the user_id from the request
            portfolio = Portfolio.objects.filter(user=user_id, is_default=True).order_by('-portfolio_id').first()

            if not portfolio:
                return JsonResponse({'success': False, 'error': 'Default portfolio not found'}, status=404)


            data = json.loads(request.body)
            views_filter = data.get('views-filter', 'Tables')
            views_value = data.get('views-value', 'overview')
            sorted_by = data.get('sortedBy', '')
            desc = data.get('desc', '')
            chart_per_line = data.get('chartPerLine', '')
            page = data.get('page', 1)  # Get the page number from the request, default to 1

            # Initialize the queryset
            # Part 1. holding_symbols
            symbols = [item.symbol.symbol for item in Holding.objects.filter(portfolio=portfolio)]

            # Get the total count of the filtered queryset
            total_count = len(symbols)

            if views_filter == 'Charts':
                # Construct the URL for the chart image
                chart_data = []
                for symbol in symbols:
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
                queryset = MarketSymbol.objects.filter(symbol__in=symbols).values('symbol', 'name', 'market', 'asset_type')

                # Paginate the results
                paginator = Paginator(queryset, 40)  # Show 10 items per page
                page_obj = paginator.get_page(page)

                return JsonResponse({
                    'results': list(page_obj),
                    'total_count': total_count
                }, safe=False, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)


def calculate_indicators(symbol):
    # Fetch historical data
    queryset = MarketStockHistoricalBarsByDay.objects.filter(symbol=symbol).order_by('time')

    df = pd.DataFrame.from_records(queryset.values('time', 'close'))

    # Set index for easier processing
    df.set_index('time', inplace=True)

    # Calculate indicators using ta-lib
    df['sma'] = talib.SMA(df['close'], timeperiod=20)
    df['rsi'] = talib.RSI(df['close'], timeperiod=14)

    upper, middle, lower = talib.BBANDS(df['close'], timeperiod=20, nbdevup=2, nbdevdn=2)
    df['bollinger_upper'] = upper
    df['bollinger_lower'] = lower

    # Save results to the database
    for date, row in df.iterrows():
        RatingIndicatorResult.objects.update_or_create(
            symbol_id=symbol,
            time=date,
            defaults={
                'sma': row['sma'],
                'rsi': row['rsi'],
                'bollinger_upper': row['bollinger_upper'],
                'bollinger_lower': row['bollinger_lower'],
            }
        )