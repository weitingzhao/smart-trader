import json
import pandas as pd
from decimal import Decimal
from django.db.models import Sum, F
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from pydantic.dataclasses import dataclass

from apps.common.models import *
from django.shortcuts import render, get_object_or_404



def default(request):
    user_id = request.user.id  # Assuming you have the user_id from the request
    portfolio = Portfolio.objects.filter(user=user_id, is_default=True).order_by('-portfolio_id').first()

    if not portfolio:
        return JsonResponse({'success': False, 'error': 'Default portfolio not found'}, status=404)

    holdings = Holding.objects.filter(portfolio=portfolio)

    # Extract symbols from portfolio items
    symbols = [item.symbol.symbol for item in holdings]

    if len(symbols) > 0:
        # get current time previous day benchmark
        benchmark = get_stock_hist_bars(True, symbols, 2)

        # current time is base on current time is stock market open hour or close hour
        # if is close hour.
        #   a. if day data is not available, need use min data.
        #       I.  if min data is not available, need use api, directly pull.
        #       II. if min data is available, need use min data.
        #   b. if day data is available, need use day data.
        latest_bar = get_stock_hist_bars(True, symbols, 1)

        # Convert the fetched rows into pandas DataFrames
        benchmark_df = pd.DataFrame(benchmark)
        latest_bar_df = pd.DataFrame(latest_bar)
        # Convert holdings to DataFrame
        holdings_df = pd.DataFrame(list(holdings.values()))

        # Step 2. Calculate dataframes
        # Merge the DataFrames on the 'symbol' column
        merged_df = pd.merge(latest_bar_df, benchmark_df, on='symbol', suffixes=('', '_bk'))
        # Merge items DataFrame with merged_df on 'symbol'
        final_df = pd.merge(holdings_df, merged_df, left_on='symbol_id', right_on='symbol')

        # Fetch and sum the quantity_final from transaction
        transaction = (Transaction.objects.filter(holding__in=holdings)
                       .annotate(amount=F('quantity_final') * F('price_final'))
                       .values('holding_id')
                       .annotate(quantity=Sum('quantity_final'), total_cost=Sum('amount')))
        transaction_df = pd.DataFrame(list(transaction), columns=['holding_id', 'quantity', 'total_cost'])

        # Merge action_df with final_df
        final_df = pd.merge(final_df, transaction_df, left_on='holding_id', right_on='holding_id', how='left').fillna(0)

        # Step 3. Calculate the total cost & market value
        final_df['market_value'] = final_df['quantity'] * final_df['close']

        # Step 4. Calculate the change since last biz day
        # Calculate the change as the difference between latest_bar.close and benchmark.close
        final_df['chg'] = final_df['close'] - final_df['close_bk']
        # Calculate change in position
        final_df['chg_position'] = final_df['quantity'] * final_df['chg']
        # Calculate the change percent
        final_df['chg_pct'] = ((final_df['chg'] / final_df['close_bk']) * 100).round(2)
        # Add a new column 'trend' based on the 'change' column
        final_df['trend'] = final_df['chg'].apply(lambda x: "UP" if x > 0 else ("DOWN" if x < 0 else "-"))

        # Step 6. Calculate the total cost & change
        # Calculate total change in value
        final_df['total_chg_position'] = final_df.apply(lambda row: (Decimal(row['market_value']) - Decimal(row['total_cost'])).quantize(Decimal('0.01')), axis=1)

        # Calculate total change percentage
        final_df['total_chg_pct'] = final_df.apply(lambda row: (
            (Decimal(row['total_chg_position']) / Decimal(row['total_cost']) * 100).quantize(Decimal('0.01')) if row['total_cost'] != 0 else Decimal('0.00')), axis=1)
        # Calculate total change trand
        final_df['total_trend'] = final_df['total_chg_position'].apply(lambda x: "UP" if x > 0 else ("DOWN" if x < 0 else "-"))



        def format(x):
            if pd.isna(x):
                return '-'
            return f"+{round(x, 2)}" if x > 0 else (f"-{abs(round(x, 2))}" if x < 0 else round(x, 2))
        # Format the change & change values
        final_df['chg_position'] = final_df['chg_position'].apply(format)
        final_df['chg'] = final_df['chg'].apply(format)
        final_df['total_chg_position'] = final_df['total_chg_position'].apply(format)
        final_df['total_chg_pct'] = final_df['total_chg_pct'].apply(format)

        # Convert the DataFrame to JSON
        final_json = final_df.to_json(orient='records')
    else:
        final_json = []

    return render(
        request = request,
        template_name='pages/position/open_positions.html',
        context= {
            'parent': 'position',
            'segment': 'open_positions',
            'portfolio': portfolio,
            'portfolio_items': final_json,
        })


def get_stock_hist_bars(is_day, symbols:list[str], row_num:int):
    table_name = 'day' if is_day else 'min'

    with connection.cursor() as cursor:
        cursor.execute(f"""
SELECT
    mk.symbol,
    mk.name as symbol_name,
    sub.date,
    main_start.open,
    main_end.close,
    sub.volume,
    sub.*
FROM
    market_symbol mk
    LEFT JOIN LATERAL(
        SELECT
            symbol,
            ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY MAX(DATE(time)) DESC) AS row_num,
            MAX(DATE(time)) AS max_date,
            DATE(time) AS date,
            MIN(time) AS start_min,
            MAX(time) AS end_min,
            SUM(volume) AS volume
        FROM
            market_stock_hist_bars_{table_name}_ts
        WHERE
            symbol IN ('{"', '".join(symbols)}')
        GROUP BY
            symbol, DATE(time)
    ) sub ON sub.symbol = mk.symbol
    LEFT JOIN market_stock_hist_bars_{table_name}_ts main_start 
        ON main_start.symbol = sub.symbol AND main_start.time = sub.start_min
    LEFT JOIN market_stock_hist_bars_{table_name}_ts main_end 
        ON main_end.symbol = sub.symbol AND main_end.time = sub.end_min
WHERE
    sub.row_num = {row_num} AND mk.symbol IN ('{"', '".join(symbols)}')
            """)
        latest_rows = cursor.fetchall()

        # Convert the fetched rows into a list of dictionaries
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in latest_rows]




def get_holding_buy_order(request, holding_buy_order_id):
    order = get_object_or_404(HoldingBuyOrder, holding_buy_order_id=holding_buy_order_id)
    data = {
        'id': order.holding_buy_order_id,
        'quantity_target': order.quantity_target,
        'price_market': order.price_market,
        'order_place_date': order.order_place_date.strftime('%Y-%m-%d')
    }
    return JsonResponse(data)

@csrf_exempt
def add_holding_buy_order(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        buy_order = HoldingBuyOrder.objects.create(
            holding_id=data['holding_id'],
            action=data['action'],
            order_place_date=data['order_place_date'],
            quantity_target=data['quantity_target'],
            price_market=data['price_market'],
            price_stop=data['price_stop'],
            price_limit=data['price_limit'],
            is_initial=data['is_initial'],
            is_additional=data['is_additional'],
            timing=data['timing']
        )
        return JsonResponse({'status': 'success', 'buy_order_id': buy_order.holding_buy_order_id})
    return JsonResponse({'status': 'failed'}, status=400)

@csrf_exempt
def edit_holding_buy_order(request, holding_buy_order_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        order = HoldingBuyOrder.objects.get(holding_buy_order_id=holding_buy_order_id)
        order.quantity_target = data.get('quantity_target')
        order.price_market = data.get('price_market')
        order.order_place_date = data.get('order_place_date')
        order.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'failed'}, status=400)

@csrf_exempt
def delete_holding_buy_order(request, holding_buy_order_id):
    if request.method == 'DELETE':
        order = HoldingBuyOrder.objects.get(holding_buy_order_id=holding_buy_order_id)
        order.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'failed'}, status=400)

def get_holding_sell_order(request, holding_sell_order_id):
    order = get_object_or_404(HoldingSellOrder, holding_sell_order_id=holding_sell_order_id)
    data = {
        'id': order.holding_sell_order_id,
        'quantity_target': order.quantity_target,
        'price_stop': order.price_stop,
        'price_limit': order.price_limit,
        'order_place_date': order.order_place_date.strftime('%Y-%m-%d')
    }
    return JsonResponse(data)

@csrf_exempt
def add_holding_sell_order(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        buy_order = HoldingSellOrder.objects.create(
            holding_id=data['holding_id'],
            action=data['action'],
            order_place_date=data['order_place_date'],
            quantity_target=data['quantity_target'],
            price_stop=data['price_stop'],
            price_limit=data['price_limit'],
            is_initial=data['is_initial'],
            good_until=data['good_until'],
            timing=data['timing']
        )
        return JsonResponse({'status': 'success', 'buy_order_id': buy_order.holding_sell_order_id})
    return JsonResponse({'status': 'failed'}, status=400)

@csrf_exempt
def edit_holding_sell_order(request, holding_sell_order_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        order = HoldingSellOrder.objects.get(holding_sell_order_id=holding_sell_order_id)
        order.quantity_target = data.get('quantity_target')
        order.price_stop = data.get('price_stop')
        order.price_limit = data.get('price_limit')
        order.order_place_date = data.get('order_place_date')
        order.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'failed'}, status=400)

@csrf_exempt
def delete_holding_sell_order(request, holding_sell_order_id):
    if request.method == 'DELETE':
        order = HoldingSellOrder.objects.get(holding_sell_order_id=holding_sell_order_id)
        order.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'failed'}, status=400)



