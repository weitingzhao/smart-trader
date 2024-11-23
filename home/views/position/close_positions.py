import json
import pandas as pd
from decimal import Decimal
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from home.templatetags.home_filter import order_price
from django.db.models import (
    F,Case, When, Value, IntegerField, Sum, Min, Max,
    FloatField, Q, BooleanField,Subquery, OuterRef)
from apps.common.models import *
from django.shortcuts import render, get_object_or_404
from logics.logic import Logic
import datetime

# Create your views here.
instance = Logic()

def default(request):
    user_id = request.user.id  # Assuming you have the user_id from the request
    portfolio = Portfolio.objects.filter(user=user_id, is_default=True).order_by('-portfolio_id').first()

    if not portfolio:
        return JsonResponse({'success': False, 'error': 'Default portfolio not found'}, status=404)

    # Step 0. holdings
    holdings = Holding.objects.filter(portfolio=portfolio)
    # Extract symbols from portfolio items
    symbols = [item.symbol.symbol for item in holdings]
    if len(symbols) <= 0:
        return render(
            request=request, template_name='pages/position/close_positions.html',
            context={'parent': 'position','segment': 'close_positions', 'portfolio': portfolio, 'portfolio_items': []})

    final_df = pd.DataFrame(list(holdings.values()))

    # Step 2. symbol:
    symbol_names = MarketSymbol.objects.filter(symbol__in=final_df['symbol_id']).values('symbol', 'name')
    symbol_names_df = pd.DataFrame(list(symbol_names))
    # Merge to final_df
    final_df = pd.merge(final_df, symbol_names_df, left_on='symbol_id', right_on='symbol', how='left')

    # Step 3. trades
    trades = (Transaction.objects.filter(holding__in=holdings)
                    .annotate(
                       trade_id=Case(
                           When(buy_order_id__isnull=False, then=F('buy_order__trade_id')),
                           When(sell_order_id__isnull=False, then=F('sell_order__trade_id')),
                           default=Value(None),
                           output_field=IntegerField()
                       ),
                       is_finished=Case(
                           When(buy_order_id__isnull=False, then=F('buy_order__trade__is_finished')),
                           When(sell_order_id__isnull=False, then=F('sell_order__trade__is_finished')),
                           default=Value(None),
                           output_field=BooleanField()
                       )
                   )
                   .filter(Q(is_finished=True))
                   .annotate(amount=F('quantity_final') * F('price_final'))
                   .values('trade_id', 'holding_id')
                   .annotate(
                        init_quantity=Sum(Case(When(transaction_type=1, then=F('quantity_final') ))),
                        quantity=Sum(Case(When(transaction_type=2, then=F('quantity_final') ))),
                        buy_total_value=Sum(Case(When(transaction_type=1, then=F('quantity_final') * F('price_final')))),
                        buy_average_price=Sum(Case(When(transaction_type=1, then=F('quantity_final') * F('price_final')))) / Sum(Case(When(transaction_type=1, then=F('quantity_final')))),
                        sell_total_value=Sum(Case(When(transaction_type=2, then=F('quantity_final') * F('price_final')))),
                        sell_average_price=Sum(Case(When(transaction_type=2, then=F('quantity_final') * F('price_final')))) / Sum(Case(When(transaction_type=2, then=F('quantity_final')))),
                        sell_commission=Sum(Case(When(transaction_type=2, then=F('commission')))),
                        entry_date=Min('date'),
                        exit_date=Max('date'),
                   ))
    trade_df = pd.DataFrame(list(trades), columns=[
        'trade_id', 'holding_id', 'init_quantity', 'quantity',
        'buy_total_value', 'buy_average_price',
        'sell_total_value', 'sell_average_price', 'sell_commission',
        'entry_date', 'exit_date'])
    # Merge Transaction into
    final_df = pd.merge(final_df, trade_df, left_on='holding_id', right_on='holding_id', how='inner').fillna(0)

    # Step 4. Get stock pre-exit-date prices
    symbol_date_pairs = [(row['symbol_id'], row['exit_date']) for index, row in final_df.iterrows()]
    # Call the get_stock_prices function
    stock_prices_df = instance.research.treading().get_stock_prices(symbol_date_pairs, -1)
    # Merge the trading prices into final_df
    final_df = pd.merge(final_df, stock_prices_df, left_on=['symbol_id', 'exit_date'], right_on=['symbol', 'date'],how='left')

    # Step 5. Query to get initial sell orders (action = 1) for each holding_id
    trade_ids = trade_df['trade_id'].tolist()
    initial_sell_orders = HoldingSellOrder.objects.filter(
        trade_id__in=trade_ids
    ).values('trade_id').annotate(
        init_sell_order_id=Min('holding_sell_order_id'),
        last_sell_order_id=Max('holding_sell_order_id')
    )
    # Convert to DataFrame
    initial_sell_orders_df = pd.DataFrame(list(initial_sell_orders))

    # get init_stop, init_limit, last_stop, and last_limit
    init_sell_order_ids = initial_sell_orders_df['init_sell_order_id'].tolist()
    last_sell_order_ids = initial_sell_orders_df['last_sell_order_id'].tolist()
    init_sell_orders = HoldingSellOrder.objects.filter(
        holding_sell_order_id__in=init_sell_order_ids
    ).values('holding_sell_order_id', 'price_stop', 'price_limit')
    last_sell_orders = HoldingSellOrder.objects.filter(
        holding_sell_order_id__in=last_sell_order_ids
    ).values('holding_sell_order_id', 'price_stop', 'price_limit')
    # Convert to DataFrame
    init_sell_orders_df = pd.DataFrame(list(init_sell_orders))
    last_sell_orders_df = pd.DataFrame(list(last_sell_orders))
    # Merge the initial and last sell orders data into initial_sell_orders_df
    initial_sell_orders_df = pd.merge(
        initial_sell_orders_df,
        init_sell_orders_df,
        left_on='init_sell_order_id',
        right_on='holding_sell_order_id',
        how='left',
        suffixes=('', '_init')
    ).drop(columns=['holding_sell_order_id'])
    initial_sell_orders_df = pd.merge(
        initial_sell_orders_df,
        last_sell_orders_df,
        left_on='last_sell_order_id',
        right_on='holding_sell_order_id',
        how='left',
        suffixes=('', '_last')
    ).drop(columns=['holding_sell_order_id'])
    # Rename columns for clarity
    initial_sell_orders_df.rename(columns={
        'price_stop': 'init_stop',
        'price_limit': 'init_limit',
        'price_stop_last': 'last_stop',
        'price_limit_last': 'last_limit'
    }, inplace=True)
    # Merge the initial and last sell orders data into final_df
    final_df = pd.merge(final_df, initial_sell_orders_df, on='trade_id', how='left')

    # Step 6. Performance
    # 6.1. Calculate the "delta day cost" column
    final_df['delta_day_cost'] = (final_df['sell_average_price'].astype(float) - final_df['close'].astype(float)) * final_df['quantity'].astype(float)
    final_df['delta_day_cost_rat'] = final_df['delta_day_cost'].astype(float) / final_df['buy_total_value'].astype(float) * 100
    final_df['trade_margin'] = final_df['sell_total_value'] - final_df['buy_total_value']
    final_df['trade_performance'] = (final_df['trade_margin'].astype(float) / final_df['buy_total_value'].astype(float)) * 100
    final_df['held_day'] = (pd.to_datetime(final_df['exit_date']) - pd.to_datetime(final_df['entry_date'])).dt.days
    # 6.2. Calculate portfolio performance
    model_capital = UserStaticSetting.objects.values_list('capital', flat=True).first()
    final_df['portfolio_trade_performance'] = final_df['trade_margin'].astype(float) / float(model_capital) * 100

    # Step 7. Risk / Gain
    final_df['last_risk'] = (
            (final_df['close'].astype(float)
             - (final_df['last_stop'].astype(float) + final_df['last_limit'].astype(float)) / 2)
            * final_df['quantity'].astype(float)
    )
    final_df['last_risk_ratio'] = (final_df['last_risk'].astype(float) / final_df['buy_total_value'].astype(
        float)) * 100

    final_df['init_risk'] = (
            (final_df['buy_average_price'].astype(float)
             - (final_df['init_stop'].astype(float) + final_df['init_limit'].astype(float)) / 2)
            * final_df['init_quantity'].astype(float)
    )
    final_df['init_risk_ratio'] = (final_df['init_risk'].astype(float) / final_df['buy_total_value'].astype(float)) * 100




    # Convert the DataFrame to JSON
    final_json = final_df.to_json(orient='records', date_format='iso')
    return render(
        request = request,
        template_name='pages/position/close_positions.html',
        context= {
            'parent': 'position',
            'segment': 'close_positions',
            'portfolio': portfolio,
            'portfolio_items': final_json,
        })
