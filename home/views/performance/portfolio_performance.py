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

    # Step 2. Get transactions
    holding_ids = holdings.values_list('holding_id', flat=True)
    transactions = Transaction.objects.filter(holding_id__in=holding_ids)
    transactions_df = pd.DataFrame(list(transactions.values()))
    # Group transactions by date and calculate daily balance
    transactions_df['date'] = pd.to_datetime(transactions_df['date']).dt.date
    transactions_df['amount'] = transactions_df.apply(
        lambda row: row['quantity_final'] * row['price_final'] if row['transaction_type'] == '1' else -row[
            'quantity_final'] * row['price_final'],
        axis=1
    )
    balance_df = transactions_df.groupby('date')['amount'].sum().reset_index()

    # Step 3. Create a full date range from the minimum date to today
    min_date = balance_df['date'].min()
    today = pd.to_datetime('today').date()
    full_date_range = pd.DataFrame({'date': pd.date_range(start=min_date, end=today)})
    full_date_range['date'] = pd.to_datetime(full_date_range['date']).dt.date

    # Merge the full date range with daily_balance_df
    balance_df = pd.merge(full_date_range, balance_df, on='date', how='left').fillna(0)
    # Calculate the total_balance
    balance_df['total_amount'] = balance_df['amount'].cumsum()

    # Last Step: Prepare the data for the chart
    labels = balance_df['date'].astype(str).tolist()
    data = balance_df['total_amount'].tolist()
    chart_data = {
        "labels": labels,
        "datasets": [{
            "label": "Mobile apps",
            "tension": 0.4,
            "borderWidth": 0,
            "pointRadius": 0,
            "borderColor": "#cb0c9f",
            "borderWidth": 3,
            "fill": True,
            "data": data,
            "maxBarThickness": 6
        }]
    }
    return JsonResponse(chart_data)


