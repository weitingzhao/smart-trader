import pandas as pd
from django.shortcuts import render
from apps.common.models import *
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import json
import pandas as pd
from decimal import Decimal
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from home.templatetags.home_filter import order_price
from django.db.models import (
    F,Case, When, Value, IntegerField, Sum, Max,
    FloatField, Q, BooleanField,Subquery, OuterRef)
from logics.logic import Logic
from apps.common.models import *
from django.shortcuts import render, get_object_or_404



def default(request):
    return render(
        request=request,
        template_name='pages/performance/portfolio_performance.html',
        context= {
            'parent': 'performance',
            'segment': 'portfolio_performance',
        })

@csrf_exempt
def get_balance_history(request):
    user_id = request.user.id  # Assuming you have the user_id from the request

    # Step 0. Get default portfolio
    portfolio = Portfolio.objects.filter(user=user_id, is_default=True).order_by('-portfolio_id').first()
    if not portfolio:
        return JsonResponse({'success': False, 'error': 'Default portfolio not found'}, status=404)

    # Step 1. Get holdings under portfolio
    holdings = Holding.objects.filter(portfolio=portfolio)
    symbols = [item.symbol.symbol for item in holdings]
    if len(symbols) <= 0:
        return render(
            request= request, template_name='pages/dashboard/overview.html',
            context={ 'parent': 'dashboard', 'segment': 'overview', 'holdings': []})
    holding_symbol_map = {holding.holding_id: holding.symbol.symbol for holding in holdings}

    # Step 2. Get transactions
    holding_ids = holdings.values_list('holding_id', flat=True)
    # Fetch transaction data
    transactions = Transaction.objects.filter(holding_id__in=holding_ids)
    transactions_df = pd.DataFrame(list(transactions.values()))
    transactions_df['date'] = pd.to_datetime(transactions_df['date']).dt.date
    transactions_df['quantity'] = transactions_df.apply(
        lambda row: row['quantity_final'] if row['transaction_type'] == '1' else -row['quantity_final'],
        axis=1
    )
    transactions_df['holding'] = transactions_df.apply(
        lambda row: row['quantity_final'] * row['price_final']
        if row['transaction_type'] == '1' else -row['quantity_final'] * row['price_final'] - row['commission'],
        axis=1
    )
    transactions_df = transactions_df.drop(columns=['buy_order_id', 'sell_order_id'])
    # Group by holding and trade_id
    transactions_df['symbol'] = transactions_df['holding_id'].map(holding_symbol_map)
    transactions_df = transactions_df.groupby(['symbol', 'date']).agg(
        quantity_sum=pd.NamedAgg(column='quantity', aggfunc='sum'),
        holding_sum=pd.NamedAgg(column='holding', aggfunc='sum'),
    ).reset_index()
    transactions_df = transactions_df.rename(columns={'quantity_sum': 'quantity'})
    transactions_df = transactions_df.rename(columns={'holding_sum': 'holding'})

    # Step 3. pivot transactions by symbol
    transactions_df = transactions_df.pivot(index='date', columns='symbol', values=['quantity', 'holding'])
    transactions_df.columns = [
        f"q/{col[1]}" if col[0] == 'quantity' else f"h/{col[1]}" for col in transactions_df.columns.values
    ]
    # Reset index to make 'date' a column again
    transactions_df = transactions_df.reset_index()
    transactions_df = transactions_df.fillna(0)

    # Step 4. Get date range from the minimum date to today and base on this range get market data
    min_date = transactions_df['date'].min()
    today = pd.to_datetime('today').date()
    # Create a DataFrame with all symbols
    symbols_df = pd.DataFrame({'symbol': symbols})
    market_data = MarketStockHistoricalBarsByDay.objects.filter(
        symbol__in=symbols,
        time__date__range=[min_date, today]
    ).values('symbol', 'time', 'close')
    # Convert market data to DataFrame
    market_data_df = pd.DataFrame(list(market_data))
    market_data_df['date'] = pd.to_datetime(market_data_df['time']).dt.date
    # Left join symbols_df with market_data_df
    full_market_data_df = pd.merge(symbols_df, market_data_df, on='symbol', how='left').fillna(0)
    # Pivot the resulting DataFrame by symbol
    full_market_data_df = full_market_data_df.pivot(index='date', columns='symbol', values='close').reset_index()

    # Merge the full date range with daily_balance_df
    balance_df = pd.merge(full_market_data_df, transactions_df, on='date', how='left').fillna(0)

    # Step 4.1 Apply cumulative sum to the pivoted columns
    for col in balance_df.columns:
        if col.startswith('q/') or col.startswith('h/'):
            balance_df[col] = balance_df[col].cumsum()
    # Step 4.2 Calculate market value for each symbol
    for symbol in symbols:
        quantity_col = f'q/{symbol}'
        if quantity_col not in balance_df.columns:
            continue
        balance_df[f'mv/{symbol}'] = balance_df[f'q/{symbol}'] * balance_df[symbol]
    # Step 4.3 Calculate balance_holding by summing all h/{symbol} columns
    balance_df['balance_holding'] = balance_df[[col for col in balance_df.columns if col.startswith('h/')]].sum(axis=1)
    # Step 4.4 Calculate balance_mv by summing all mv/{symbol} columns
    balance_df['balance_mv'] = balance_df[[col for col in balance_df.columns if col.startswith('mv/')]].sum(axis=1)

    # Step 5. Get funding records
    funding_records = Funding.objects.filter(portfolio=portfolio)
    funding_df = pd.DataFrame(list(funding_records.values()))
    funding_df['completion_date'] = pd.to_datetime(funding_df['completion_date']).dt.date
    funding_df = funding_df.rename(columns={'completion_date': 'date', 'amount': 'funding'})
    balance_df = pd.merge(balance_df, funding_df[['date', 'funding']], on='date', how='left').fillna(0)

    # Step 6. Get cash balance records
    cash_balances = CashBalance.objects.filter(portfolio=portfolio)
    cash_balance_df = pd.DataFrame(list(cash_balances.values()))
    cash_balance_df['as_of_date'] = pd.to_datetime(cash_balance_df['as_of_date']).dt.date
    cash_balance_df['cash_mm'] = cash_balance_df['money_market'] + cash_balance_df['cash']
    cash_balance_df = cash_balance_df.rename(columns={'as_of_date': 'date'})
    # Forward fill the cash_mm values to fill any missing dates
    balance_df = pd.merge(balance_df, cash_balance_df[['date', 'cash_mm', 'money_market','cash']], on='date', how='left').fillna(0)

    # Step 7. Calculate column under balance_df
    # Calculate the cash & money market
    balance_df['cash_mm_daily'] = balance_df['cash_mm'].replace(0, pd.NA).ffill().fillna(0)
    balance_df = balance_df.drop(columns=['cash_mm'])
    # balance_df['funding']
    # Calculate total capital and market value
    balance_df['total_market'] = balance_df['balance_mv'].apply(Decimal) + balance_df['cash_mm_daily']
    balance_df['total_asset'] = balance_df['balance_holding'] + balance_df['cash_mm_daily']
    balance_df['total_invest'] = balance_df['balance_holding']

    # Last Step: Prepare the data for the chart
    labels = balance_df['date'].astype(str).tolist()

    market_data = balance_df['total_market'].tolist()
    asset_data = balance_df['total_asset'].tolist()
    invest_data = balance_df['total_invest'].tolist()

    chart_data = {
        "labels": labels,
        "datasets": [{
            "label": "market",
            "tension": 0.4,
            "borderWidth": 0,
            "pointRadius": 0,
            "borderColor": "#cb0c9f",
            "borderWidth": 3,
            "fill": True,
            "data": market_data,
            "maxBarThickness": 6
        }, {
            "label": "assets",
            "tension": 0.4,
            "borderWidth": 0,
            "pointRadius": 0,
            "borderColor": "#3A416F",
            "borderWidth": 3,
            "fill": True,
            "data": asset_data,
            "maxBarThickness": 6
        }, {
            "label": "invest",
            "tension": 0.4,
            "borderWidth": 0,
            "pointRadius": 0,
            "borderColor": "#16ce38",
            "borderWidth": 3,
            "fill": True,
            "data": invest_data,
            "maxBarThickness": 6
        }],
    }
    return JsonResponse(chart_data)


