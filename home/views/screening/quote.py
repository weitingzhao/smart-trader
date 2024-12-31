from home.forms.portfolio import *
from django.shortcuts import render
from apps.common.models import *
from django.db.models import F,Case, When, Value, IntegerField, Sum, FloatField, Q, BooleanField
from django.db.models.functions import Cast


def default(request, symbol):

    symbol = MarketSymbol.objects.select_related("stock").get(symbol=symbol)
    if symbol is None:
        return render(request, 'accounts/error/404.html')

    stock = symbol.stock

    # Retrieve the portfolio related to the symbol
    portfolio = Portfolio.objects.filter(user=request.user.id, is_default=True).order_by('-portfolio_id').first()
    # Retrieve the holding related to the portfolio
    holding = Holding.objects.filter(portfolio=portfolio, symbol=symbol).first()

    # Step 1.
    # 1.a Retrieve Orders
    buy_orders = (Order.objects.filter(holding=holding, order_style=1).annotate(
        filled_quantity=Sum(
            'transaction__quantity_final',
            filter=Q(transaction__order_id=F('order_id')),
            output_field=FloatField()
        ),
        filled_rate=F('filled_quantity') / Cast(F('quantity_target'), FloatField()) * 100,
        is_filled=Case(
            When(
                Q(filled_rate__gte=100),
                then=Value(True)
            ),
            default=Value(False),
            output_field=BooleanField()
        ),
        is_finished=F('trade__is_finished')
    ).order_by('-order_id'))

    sell_orders = (Order.objects.filter(holding=holding, order_style=2).annotate(
        filled_quantity=Sum(
            'transaction__quantity_final',
            filter=Q(transaction__order_id=F('order_id')),
            output_field=FloatField()
        ),
        filled_rate=F('filled_quantity') / Cast(F('quantity_target'), FloatField()) * 100,
        is_filled=Case(
            When(
                Q(filled_rate__gte=100),
                then=Value(True)
            ),
            default=Value(False),
            output_field=BooleanField()
        ),
        is_finished=F('trade__is_finished')
    ).order_by('-order_id'))

    # 1.b Retrieve transaction
    transaction = Transaction.objects.filter(holding=holding).annotate(
        is_finished=F('trade__is_finished')
    ).order_by('-transaction_id')

    # 1.c Retrieve trade
    trade_ids = (Order.objects.filter(holding=holding)
                 .values('trade_id').distinct().order_by('-trade_id'))

    form_order = OrderForm()

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
        'form_order': form_order,
        'holding': holding,
        'buy_orders': buy_orders,
        'sell_orders': sell_orders,
        'transactions': transaction,
        'trade_ids': trade_ids
    }
    return render(request, 'pages/screening/quote.html', context)