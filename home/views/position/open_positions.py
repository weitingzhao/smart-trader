import json
import pandas as pd
from decimal import Decimal
from django.db.models import Sum, F
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

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
        # Convert PortfolioItem queryset to DataFrame
        items_df = pd.DataFrame(list(holdings.values()))

        # Step 2. Calculate dataframes
        # Merge the DataFrames on the 'symbol' column
        merged_df = pd.merge(latest_bar_df, benchmark_df, on='symbol', suffixes=('', '_bk'))
        # Merge items DataFrame with merged_df on 'symbol'
        final_df = pd.merge(items_df, merged_df, left_on='symbol_id', right_on='symbol')

        # Fetch and sum the quantity_final from holding_buy_action and holding_sell_action
        # Get column names using model's meta options
        buy_actions_column_names = [field.name for field in HoldingBuyAction._meta.fields]
        buy_actions = (HoldingBuyAction.objects.filter(holding__in=holdings).values('holding_id').annotate(
            total_buy=Sum('quantity_final'),
            total_buy_price=Sum(F('quantity_final') * F('price_final'))
        ))
        sell_actions_column_names = [field.name for field in HoldingSellAction._meta.fields]
        sell_actions = (HoldingSellAction.objects.filter(holding__in=holdings).values('holding_id').annotate(
            total_sell=Sum('quantity_final'),
            total_sell_price=Sum(F('quantity_final') * F('price_final'))
        ))

        buy_df = pd.DataFrame(list(buy_actions), columns=['holding_id', 'total_buy', 'total_buy_price'])
        sell_df = pd.DataFrame(list(sell_actions), columns=['holding_id', 'total_sell', 'total_sell_price'])

        # Merge buy and sell dataframes
        action_df = pd.merge(buy_df, sell_df, on='holding_id', how='outer').fillna(0)
        action_df['quantity'] = action_df['total_buy'] - action_df['total_sell']
        action_df['total_price'] = action_df['total_buy_price'] - action_df['total_sell_price']

        # Merge action_df with final_df
        final_df = pd.merge(final_df, action_df, left_on='holding_id', right_on='holding_id', how='left').fillna(0)

        # Step 3. Calculate the total cost & market value
        final_df['total_cost'] = final_df.apply(lambda row: Decimal(row['total_price']) * Decimal(row['quantity']), axis=1)
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
        final_df['total_chg_position'] = final_df.apply(lambda row: Decimal(row['market_value']) - Decimal(row['total_cost']), axis=1)
        # Calculate total change percentage
        final_df['total_chg_pct'] = final_df.apply(lambda row: ((row['total_chg_position'] / row['total_cost']) * 100).round(2) if row['total_cost'] != 0 else 0, axis=1)
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



def add_holding(request, pk):
    portfolio = get_object_or_404(Portfolio, pk=pk)
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            symbol = data.get('symbol')

            if not symbol:
                return JsonResponse({'success': False, 'error': 'symbol is missing'}, status=400)

            market_symbol = MarketSymbol.objects.filter(symbol=symbol).first()
            if not market_symbol:
                return JsonResponse({'success': False, 'error': 'Symbol not found in database'}, status=404)

            # Check if the PortfolioItem already exists
            item, created = PortfolioItem.objects.update_or_create(
                portfolio=portfolio,
                symbol=market_symbol,
                defaults={'symbol': market_symbol}
            )

            if created:
                message = 'Item added successfully'
            else:
                message = 'Item updated successfully'

            return JsonResponse({'success': True, 'message': message})
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)


@csrf_exempt
def add_holding_buy_action(request, holding_buy_order_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        quantity_final = data.get('quantity_final')
        price_final = data.get('price_final')
        date = data.get('date')

        # Get the holding_buy_order record
        order = HoldingBuyOrder.objects.get(holding_buy_order_id=holding_buy_order_id)

        if order.holding_buy_action_id:
            # Update existing holding_buy_action
            action = HoldingBuyAction.objects.get(holding_buy_action_id=order.holding_buy_action_id)
            action.date = date
            action.quantity_final = quantity_final
            action.price_final = price_final
            action.save()
        else:
            # Create new holding_buy_action
            action = HoldingBuyAction.objects.create(
                holding_id=order.holding_id,
                date=date,
                quantity_final=quantity_final,
                price_final=price_final
            )
            # Update holding_buy_order record
            order.holding_buy_action_id = action.holding_buy_action_id
            order.save()

        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'failed'}, status=400)

@csrf_exempt
def add_holding_sell_action(request, holding_buy_order_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        quantity_final = data.get('quantity_final')
        price_final = data.get('price_final')
        date = data.get('date')
        commission = data.get('commission')

        # Get the holding_sell_order record
        order = HoldingSellOrder.objects.get(holding_sell_order_id=holding_buy_order_id)

        if order.holding_sell_action_id:
            # Update existing holding_sell_action
            action = HoldingSellAction.objects.get(holding_sell_order_id=order.holding_sell_action_id)
            action.date = date
            action.quantity_final = quantity_final
            action.price_final = price_final
            action.commission = commission
            action.save()
        else:
            # Create new holding_sell_action
            action = HoldingSellAction.objects.create(
                holding_id=order.holding_id,
                date=date,
                quantity_final=quantity_final,
                price_final=price_final,
                commission=commission
            )
            # Update holding_sell_order record
            order.holding_sell_action_id = action.holding_sell_action_id
            order.save()

        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'failed'}, status=400)


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


def get_holding_buy_action(request, holding_buy_action_id):
    action = get_object_or_404(HoldingBuyAction, holding_buy_action_id=holding_buy_action_id)
    data = {
        'id': action.holding_buy_action_id,
        'quantity_final': action.quantity_final,
        'price_final': action.price_final,
        'date': action.date.strftime('%Y-%m-%d')
    }
    return JsonResponse(data)

@csrf_exempt
def edit_holding_buy_action(request, holding_buy_action_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        action = HoldingBuyAction.objects.get(holding_buy_action_id=holding_buy_action_id)
        action.quantity_final = data.get('quantity_final')
        action.price_final = data.get('price_final')
        action.date = data.get('date')
        action.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'failed'}, status=400)

@csrf_exempt
def delete_holding_buy_action(request, holding_buy_action_id):
    if request.method == 'DELETE':
        action = HoldingBuyAction.objects.get(holding_buy_action_id=holding_buy_action_id)

        order = HoldingBuyOrder.objects.get(holding_buy_action_id=holding_buy_action_id)
        order.holding_buy_action_id = None
        order.save()

        action.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'failed'}, status=400)

def get_holding_sell_action(request, holding_sell_action_id):
    action = get_object_or_404(HoldingSellAction, holding_sell_action_id=holding_sell_action_id)
    data = {
        'id': action.holding_sell_action_id,
        'quantity_final': action.quantity_final,
        'price_final': action.price_final,
        'date': action.date.strftime('%Y-%m-%d'),
        'commission': action.commission
    }
    return JsonResponse(data)

@csrf_exempt
def edit_holding_sell_action(request, holding_sell_action_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        action = HoldingSellAction.objects.get(holding_sell_action_id=holding_sell_action_id)
        action.quantity_final = data.get('quantity_final')
        action.price_final = data.get('price_final')
        action.date = data.get('date')
        action.commission = data.get('commission')
        action.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'failed'}, status=400)

@csrf_exempt
def delete_holding_sell_action(request, holding_sell_action_id):
    if request.method == 'DELETE':
        action = HoldingSellAction.objects.get(holding_sell_action_id=holding_sell_action_id)

        order = HoldingSellOrder.objects.get(holding_sell_action_id=holding_sell_action_id)
        order.holding_sell_action_id = None
        order.save()

        action.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'failed'}, status=400)






# /////obsolete
def transaction_history(request, pk):
    item = get_object_or_404(PortfolioItem, pk=pk)
    transactions = Transaction.objects.filter(portfolio_item=item)
    return render(request, 'pages/position/transaction_history.html', {'item': item, 'transactions': transactions})

def add_transaction(request):
    if request.method == 'POST':
        symbol = request.POST.get('symbol')
        quantity = request.POST.get('quantity')
        type = request.POST.get('type')
        price = request.POST.get('price')
        date = request.POST.get('date')
        commission = request.POST.get('commission', None)
        notes = request.POST.get('notes',None)

        if commission == '':
            commission = None

        try:
            portfolio_item = PortfolioItem.objects.get(symbol__symbol=symbol)
            Transaction.objects.create(
                portfolio_item=portfolio_item,
                transaction_type=type,
                quantity=quantity,
                price=price,
                date=date,
                commission=commission,
                notes=notes
            )

            # Recalculate total quantity and average price
            transactions = Transaction.objects.filter(portfolio_item=portfolio_item)
            total_quantity = sum(t.quantity if t.transaction_type == 'buy' else -t.quantity for t in transactions)
            total_cost = sum(t.quantity * t.price if t.transaction_type == 'buy' else -t.quantity * t.price for t in transactions)
            average_price = total_cost / total_quantity if total_quantity != 0 else 0

            # Update the portfolio item
            portfolio_item.quantity = total_quantity
            portfolio_item.average_price = average_price
            portfolio_item.save()

            return JsonResponse({'success': True})
        except PortfolioItem.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Portfolio item not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def delete_transaction(request, transaction_id):
    if request.method == 'DELETE':
        # Logic to delete the basket
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)

def get_transaction_history(request, portfolio_id, portfolio_item_id):
    try:
        portfolio = get_object_or_404(Portfolio, pk=portfolio_id)
        portfolio_item = get_object_or_404(PortfolioItem, pk=portfolio_item_id, portfolio=portfolio)
        transactions = Transaction.objects.filter(portfolio_item=portfolio_item).values('date', 'transaction_type', 'quantity', 'price')
        transactions_list = list(transactions)
        return JsonResponse({'transactions': transactions_list})
    except Portfolio.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Portfolio not found'}, status=404)
    except PortfolioItem.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Portfolio item not found'}, status=404)