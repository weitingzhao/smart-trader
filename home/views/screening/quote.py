import pandas as pd
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from home.forms.portfolio import *
from logics.logic import Logic
from django.shortcuts import render
from apps.common.models import *
from django.db.models import F,Case, When, Value, IntegerField
import json

from logics.utilities.dates import Dates


def default(request, symbol):

    symbol = MarketSymbol.objects.select_related("stock").get(symbol=symbol)
    if symbol is None:
        return render(request, 'accounts/error/404.html')

    stock = symbol.stock

    # Retrieve the portfolio related to the symbol
    portfolio = Portfolio.objects.filter(user=request.user.id, is_default=True).order_by('-portfolio_id').first()
    # Retrieve the holding related to the portfolio
    holding = Holding.objects.filter(portfolio=portfolio, symbol=symbol).first()
    # Retrieve all holding_buy_order and holding_sell_order records related to the holding
    holding_buy_orders = HoldingBuyOrder.objects.filter(holding=holding)
    holding_sell_orders = HoldingSellOrder.objects.filter(holding=holding)
    # Retrieve holding_buy_action data
    transaction = Transaction.objects.filter(holding=holding).annotate(
        trade_id=Case(
            When(buy_order_id__isnull=False, then=F('buy_order__trade_id')),
            When(sell_order_id__isnull=False, then=F('sell_order__trade_id')),
            default=Value(None),
            output_field=IntegerField()
        ),
        order_id = Case(
            When(buy_order_id__isnull=False, then=F('buy_order_id')),
            When(sell_order_id__isnull=False, then=F('sell_order_id')),
            default=Value(None),
            output_field=IntegerField()
        )
    )

    # Retrieve distinct trader_id from holding_buy_order based on holding_id
    trade_ids = HoldingBuyOrder.objects.filter(holding=holding).values('trade_id').distinct()

    form_buy_order = HoldingBuyOrderForm()
    form_sell_order = HoldingSellOrderForm()

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
        },
        'form_buy_order': form_buy_order,
        'form_sell_order': form_sell_order,
        'holding': holding,
        'holding_buy_orders': holding_buy_orders,
        'holding_sell_orders': holding_sell_orders,
        'transactions': transaction,
        'trade_ids': trade_ids
    }
    return render(request, 'pages/screening/quote.html', context)