import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from home.templatetags.home_filter import order_price
from django.db.models import (Sum)
from logics.logic import Logic
from apps.common.models import *
from django.shortcuts import render, get_object_or_404

# Create your views here.
instance = Logic()

def default(request):

    user_id = request.user.id  # Assuming you have the user_id from the request
    portfolio = Portfolio.objects.filter(user=user_id, is_default=True).order_by('-portfolio_id').first()

    if not portfolio:
        return JsonResponse({'success': False, 'error': 'Default portfolio not found'}, status=404)

    ##### Calculate Open Position ##############
    final_df, max_date = instance.research.position().Open().Position(portfolio)

    if final_df is not None:
        # Convert the DataFrame to JSON
        final_json = final_df.to_json(orient='records', date_format='iso')

        ##### Calculate the summary tab##############
        # Extract symbols from portfolio items
        symbols = [item.symbol.symbol for item in Holding.objects.filter(portfolio=portfolio)]

        # Step 1. calculate Market Value change
        mv = final_df['market'].sum() + final_df['delta'].sum()
        mv_bk = final_df['bk_market'].sum()
        mv_chg = mv - mv_bk
        mv_chg_pct = mv_chg / mv_bk * 100

        # Step 2. calculate Assets change
        # Merge cash_balance_df with final_df on date and date_bk
        max_date = pd.to_datetime(final_df['date'].max())
        max_date_bk = pd.to_datetime(final_df['bk_date'].max())

        cash_balance_df = instance.research.position().Open().get_cash_balance_by_date(max_date)

        today_cash_mm = cash_balance_df[cash_balance_df['cash_date'] == max_date]['cash_mm'].values[0]
        today_cash_bk = cash_balance_df[cash_balance_df['cash_date'] == max_date_bk]['cash_mm'].values[0]

        assets = mv + float(today_cash_mm)
        assets_bk = mv_bk + float(today_cash_bk)
        assets_chg = assets - assets_bk
        assets_chg_pct = assets_chg / assets_bk * 100

        # Join symbols with a comma separator
        summary = {
            # Holding Symbols
            'holding_symbols': '|'.join(symbols),
            # Market Value
            'mv': mv,
            'mv_chg': mv_chg,
            'mv_chg_pct': mv_chg_pct,
            # Assets
            'assets': assets,
            'assets_chg': assets_chg,
            'assets_chg_pct': assets_chg_pct,
            # Add other context variables here
        }
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
            'summary': summary
        })

def get_holding_buy_order(request, holding_buy_order_id):
    order = get_object_or_404(HoldingBuyOrder, holding_buy_order_id=holding_buy_order_id)
    data = {
        'id': order.holding_buy_order_id,
        'ref_order_id': order.ref_buy_order_id,

        'action': order.action,
        'order_type': order.order_type,

        'quantity_target': order.quantity_target,
        'price_market': order.price_market,
        'price_stop': order.price_stop,
        'price_limit': order.price_limit
    }
    return JsonResponse(data)

def get_holding_buy_ref_order(request, ref_buy_order_id):
    orders = HoldingBuyOrder.objects.filter(ref_buy_order_id=ref_buy_order_id)
    data = [
        {
            'id': order.holding_buy_order_id,
            'ref_order_id': order.ref_buy_order_id,

            'action': order.action,
            'order_type': order.order_type,

            'quantity_target': order.quantity_target,
            'price_market': order.price_market,
            'price_stop': order.price_stop,
            'price_limit': order.price_limit,
            'price': order_price(None,order)
        }
        for order in orders
    ]
    return JsonResponse(data, safe=False)


@csrf_exempt
def add_holding_buy_order(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        trade_id = None
        ref_buy_order_id = None
        if data['action'] == '1':
            trade = Trade.objects.create(
                profit_actual=0,
                profit_actual_ratio=0,
            )
            trade_id = trade.trade_id
        elif data['action'] == '2':
            ref_buy_order_id = data['ref_order_id']
            trade_id = HoldingBuyOrder.objects.get(holding_buy_order_id=ref_buy_order_id).trade_id

        buy_order = HoldingBuyOrder.objects.create(
            holding_id=data['holding_id'],
            trade_id=trade_id,
            ref_buy_order_id=ref_buy_order_id,

            action=data['action'],
            timing=data['timing'],

            order_type=data['order_type'],
            quantity_target=data['quantity_target'],
            price_market=data['price_market'] if data['price_market'] != '' else None,
            price_stop= data['price_stop'] if data['price_stop'] != '' else None,
            price_limit=data['price_limit'] if data['price_limit'] != '' else None,
        )
        return JsonResponse({'status': 'success', 'buy_order_id': buy_order.holding_buy_order_id})
    return JsonResponse({'status': 'failed'}, status=400)

@csrf_exempt
def add_holding_sell_order(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        buy_order = HoldingSellOrder.objects.create(
            holding_id=data['holding_id'],

            action=data['action'],
            timing=data['timing'],

            trade_id=data['trade_id'],
            ref_sell_order_id=data['ref_order_id'],

            order_type=data['order_type'],
            quantity_target=data['quantity_target'],
            price_market=data['price_market'] if data['price_market'] != '' else None,
            price_stop= data['price_stop'] if data['price_stop'] != '' else None,
            price_limit=data['price_limit'] if data['price_limit'] != '' else None,

            order_place_date=data['order_place_date'],
        )
        return JsonResponse({'status': 'success', 'sell_order_id': buy_order.holding_sell_order_id})
    return JsonResponse({'status': 'failed'}, status=400)



@csrf_exempt
def edit_holding_buy_order(request, holding_buy_order_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        order = HoldingBuyOrder.objects.get(holding_buy_order_id=holding_buy_order_id)
        order.action = data.get('action')

        order.order_type = data.get('order_type')
        order.quantity_target = data.get('quantity_target')
        order.price_market = data.get('price_market') if data.get('price_market') != '' else None
        order.price_stop = data.get('price_stop') if data.get('price_stop') != '' else None
        order.price_limit = data.get('price_limit') if data.get('price_limit') != '' else None

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

        'action': order.action,
        'trade_id': order.trade_id,
        'ref_order_id': order.ref_sell_order_id,

        'order_type': order.order_type,
        'quantity_target': order.quantity_target,
        'price_market': order.price_market,
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

        order.action = data.get('action')
        order.trade_id = data.get('trade_id')
        order.ref_sell_order_id = data.get('ref_order_id')

        order.order_type = data.get('order_type')
        order.quantity_target = data.get('quantity_target')
        order.price_market = data.get('price_market') if data.get('price_market') != '' else None
        order.price_stop = data.get('price_stop') if data.get('price_stop') != '' else None
        order.price_limit = data.get('price_limit') if data.get('price_limit') != '' else None

        order.order_place_date = data.get('order_place_date')
        order.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'failed'}, status=400)

@csrf_exempt
def adjust_holding_sell_order(request, holding_sell_order_id):
    if request.method == 'POST':
        data = json.loads(request.body)

        # Retrieve the existing sell order and mark it as obsolete
        existing_order = HoldingSellOrder.objects.get(holding_sell_order_id=data['sell_order_id'])
        existing_order.is_obsolete = True
        existing_order.save()

        # Create a new sell order with the provided details
        if existing_order.price_stop is not None and data['price_stop'] != '':
            if float(data['price_stop']) >= float(existing_order.price_stop):
                action = ActionChoices.Active_RAISE_Stop_Bar
            else:
                action = ActionChoices.Active_LOWER_Stop_Bar
        else:
            action = ActionChoices.NONE

        new_order = HoldingSellOrder.objects.create(
            holding_id=existing_order.holding_id,
            trade_id=existing_order.trade_id,
            ref_sell_order_id=existing_order.holding_sell_order_id,

            action=action,
            timing=existing_order.timing,

            order_type=existing_order.order_type,
            quantity_target=data['quantity_target'],
            price_stop=data['price_stop'] if data['price_stop'] != '' else None,
            price_limit=data['price_limit'] if data['price_limit'] != '' else None,

            order_place_date=data['order_place_date'] if data['order_place_date'] != '' else existing_order.order_place_date,
            is_obsolete=False
        )

        return JsonResponse({'status': 'success', 'new_sell_order_id': new_order.holding_sell_order_id})
    return JsonResponse({'status': 'failed'}, status=400)

@csrf_exempt
def delete_holding_sell_order(request, holding_sell_order_id):
    if request.method == 'DELETE':
        order = HoldingSellOrder.objects.get(holding_sell_order_id=holding_sell_order_id)
        order.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'failed'}, status=400)

def trade_calculate(request, trade_id):
    trade = get_object_or_404(Trade, trade_id=trade_id)
    # Get all buy and sell orders for the trade
    buy_orders = HoldingBuyOrder.objects.filter(trade_id=trade_id)
    sell_orders = HoldingSellOrder.objects.filter(trade_id=trade_id)

    # Get all transactions related to the buy and sell orders
    buy_transactions = Transaction.objects.filter(buy_order_id__in=buy_orders.values_list('holding_buy_order_id', flat=True))
    sell_transactions = Transaction.objects.filter(sell_order_id__in=sell_orders.values_list('holding_sell_order_id', flat=True))

    # Sum the quantity_final for buy and sell transactions
    buy_quantity_sum = buy_transactions.aggregate(total=Sum('quantity_final'))['total'] or 0
    sell_quantity_sum = sell_transactions.aggregate(total=Sum('quantity_final'))['total'] or 0

    # Calculate the net quantity
    net_quantity = buy_quantity_sum - sell_quantity_sum

    # Update the trade's is_finished status
    trade.is_finished = (net_quantity == 0)
    trade.save()

    data = {
        'id': trade.trade_id,
        'profit_actual': trade.profit_actual,
        'profit_actual_ratio': trade.profit_actual_ratio,
        'is_finished': trade.is_finished,
    }
    return JsonResponse(data)
