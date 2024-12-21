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

    if final_df is None:
        summary = {}
        final_json = []
    else:
        ##### Calculate the summary tab ##############
        summary = instance.research.position().Open().summary(portfolio, final_df)
        # Convert the DataFrame to JSON
        final_json = final_df.to_json(orient='records', date_format='iso')

        # Save open_summary to portfolio investment column
        portfolio.investment = summary['mv']['value']
        portfolio.save()

    return render(
        request = request,
        template_name='pages/position/open_positions.html',
        context= {
            'parent': 'position',
            'segment': 'open_positions',
            'portfolio': portfolio,
            'portfolio_items': final_json,
            'summary': summary,
            'trade_source_choices': TradeSourceChoices.choices,
            'trade_phase_choices': TradePhaseChoices.choices,
            'trade_phase_rating_choices': TradePhaseRatingChoices.choices,
            'page_title': 'Open Position'  # title
        })

def get_order(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    data = {
        'id': order.order_id,

        'action': order.action,
        'trade_id': order.trade_id,
        'ref_order_id': order.ref_order_id,

        'order_style': order.order_style,
        'order_type': order.order_type,
        'quantity_target': order.quantity_target,
        'price_market': order.price_market,
        'price_stop': order.price_stop,
        'price_limit': order.price_limit,

        'order_place_date': order.order_place_date.strftime('%Y-%m-%d')
    }

    return JsonResponse(data)

def get_order_ref(request, order_id):
    orders = Order.objects.filter(ref_order_id=order_id)
    data = [
        {
            'id': order.order_id,
            'ref_order_id': order.ref_order_id,

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
def add_order(request):
    if request.method == 'POST':
        data = json.loads(request.body)




        trade_id = None
        ref_order_id = None
        if data['action'] == '1':
            if data["order_style"] == '1':
                trade = Trade.objects.create(
                    profit_actual=0,
                    profit_actual_ratio=0,
                )
                trade_id = trade.trade_id
            else:
                trade_id = data["trade_id"]

        elif data['action'] == '2':
            ref_order_id = data['ref_order_id']
            trade_id = Order.objects.get(order_id=ref_order_id).trade_id

        order = Order.objects.create(
            holding_id=data['holding_id'],
            ref_order_id=ref_order_id,
            trade_id=trade_id,

            order_style=data['order_style'],
            order_type=data['order_type'],
            quantity_target=data['quantity_target'],
            price_market=data['price_market'] if data['price_market'] != '' else None,
            price_stop= data['price_stop'] if data['price_stop'] != '' else None,
            price_limit=data['price_limit'] if data['price_limit'] != '' else None,

            order_place_date=data['order_place_date'],

            action=data['action'],
            timing=data['timing'],
        )
        return JsonResponse({'status': 'success', 'order_id': order.order_id})
    return JsonResponse({'status': 'failed'}, status=400)



@csrf_exempt
def edit_order(request, order_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        order = Order.objects.get(order_id=order_id)

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
def delete_order(request, order_id):
    if request.method == 'DELETE':
        order = Order.objects.get(order_id=order_id)
        order.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'failed'}, status=400)


@csrf_exempt
def adjust_order(request, order_id):
    if request.method == 'POST':
        data = json.loads(request.body)

        # Retrieve the existing sell order and mark it as obsolete
        existing_order = Order.objects.get(order_id=order_id)
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

        new_order = Order.objects.create(
            holding_id=existing_order.holding_id,
            trade_id=existing_order.trade_id,
            order_style=2,
            ref_order_id=existing_order.order_id,

            action=action,
            timing=existing_order.timing,

            order_type=existing_order.order_type,
            quantity_target=data['quantity_target'],
            price_stop=data['price_stop'] if data['price_stop'] != '' else None,
            price_limit=data['price_limit'] if data['price_limit'] != '' else None,

            order_place_date=data['order_place_date'] if data['order_place_date'] != '' else existing_order.order_place_date,
            is_obsolete=False
        )

        return JsonResponse({'status': 'success', 'new_sell_order_id': new_order.order_id})
    return JsonResponse({'status': 'failed'}, status=400)



def trade_calculate(request, trade_id):
    trade = get_object_or_404(Trade, trade_id=trade_id)
    # Get all buy and sell orders for the trade
    buy_orders = Order.objects.filter(trade_id=trade_id, order_style=1)
    sell_orders = Order.objects.filter(trade_id=trade_id, order_style=2)

    # Get all transactions related to the buy and sell orders
    buy_transactions = Transaction.objects.filter(order__in=buy_orders)
    sell_transactions = Transaction.objects.filter(order__in=sell_orders)

    # Sum the quantity_final for buy and sell transactions
    buy_quantity = buy_transactions.aggregate(total=Sum('quantity_final'))['total'] or 0
    sell_quantity = sell_transactions.aggregate(total=Sum('quantity_final'))['total'] or 0

    # Calculate the net quantity
    net_quantity = buy_quantity - sell_quantity

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
