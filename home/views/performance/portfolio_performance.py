import pandas as pd
from decimal import Decimal
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from home.templatetags.home_filter import order_price
from django.db.models import (
    F,Case, When, Value, IntegerField, Sum, Max,
    FloatField, Q, BooleanField,Subquery, OuterRef)
from logics.logic import Logic
from apps.common.models import *
from django.shortcuts import render, get_object_or_404

# Create your views here.
instance = Logic()

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

    # Step 0. Check input parameters
    user_id = request.user.id  # Assuming you have the user_id from the request
    portfolio = Portfolio.objects.filter(user=user_id, is_default=True).order_by('-portfolio_id').first()

    if not portfolio:
        return JsonResponse({'success': False, 'error': 'Default portfolio not found'}, status=404)

    as_of_date_str = request.GET.get('as_of_date')
    if not as_of_date_str:
        return JsonResponse({'success': False, 'error': 'as of date is not found'}, status=404)
    try:
        as_of_date = datetime.strptime(as_of_date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'success': False, 'error': 'Invalid date format'}, status=400)

    # Step 1. Main: Get the balance history
    data_df = instance.research.position().Portfolio().balance_history(portfolio, as_of_date)

    # Step 2. Extract: Prepare the data for the chart
    # Step 2.a chart
    labels = data_df['date'].astype(str).tolist()
    market_data = data_df['total_market'].round(0).astype(int).tolist()
    asset_data = data_df['total_asset'].round(0).astype(int).tolist()
    invest_data = data_df['total_invest'].round(0).astype(int).tolist()
    baseline_data = data_df['total_baseline'].round(0).astype(int).tolist()

    # Step 2.b summary
    # Get the first and last rows of data_df
    first_row = data_df.iloc[0]
    last_row = data_df.iloc[-1]

    # Calculate the sum of funding
    funding = data_df['funding'].sum()

    # Calculate differences
    margin = round(last_row['total_market'] - first_row['total_market'] - funding, 0)
    capital = round(last_row['total_asset'] - first_row['total_asset'] - funding, 0)

    # Calculate growth rates
    margin_pct = round((margin / first_row['total_market']) * 100, 2)
    capital_pct = round((capital / first_row['total_asset']) * 100, 2)


    data = {
        "summary": {
            'funding': funding,
            "margin": margin,
            "margin_pct": margin_pct,
            "capital": capital,
            "capital_pct": capital_pct
        },
        "data": {
            "labels": labels,
            "datasets": [
                {
                    "label": "market",
                    "tension": 0,
                    "pointRadius": 0,
                    "borderColor": "#3A416F",
                    "borderWidth": 3,
                    "fill": True,
                    "data": market_data,
                    "maxBarThickness": 6
                }, {
                    "label": "assets",
                    "tension": 0,
                    "pointRadius": 0,
                    "borderColor": "#cb0c9f",
                    "borderWidth": 3,
                    "fill": True,
                    "data": asset_data,
                    "maxBarThickness": 6
                }, {
                    "label": "invest",
                    "tension": 0,
                    "pointRadius": 0,
                    "borderColor": "#17c1e8",
                    "borderWidth": 3,
                    "fill": True,
                    "data": invest_data,
                    "maxBarThickness": 6
                }, {
                "label": "baseline",
                "tension": 0.1,
                "pointRadius": 0,
                "borderColor": "rgb(75, 192, 192)",
                "borderWidth": 2,
                "fill": False,
                "data": baseline_data,
                 "borderDash": [5, 5],  #This creates a dotted line(5px dash, 5px gap)
                }
            ]
        }
    }
    return JsonResponse(data)

@csrf_exempt
def get_balance_calendar(request):

    user_id = request.user.id  # Assuming you have the user_id from the request
    portfolio = Portfolio.objects.filter(user=user_id, is_default=True).order_by('-portfolio_id').first()

    if not portfolio:
        return JsonResponse({'success': False, 'error': 'Default portfolio not found'}, status=404)

    data_df = instance.research.position().Portfolio().balance_calendar(portfolio)

    # Get the minimum date from balance_df
    initial_date = datetime.today().replace(day=1).strftime('%Y-%m-%d')

    # Create events based on balance_df
    events = []
    for _, row in data_df.iterrows():
        events.append({
            "title": f"$ {round(row['margin_diff'], 0)}",
            "start": row['date'].strftime('%Y-%m-%d'),
            "end": row['date'].strftime('%Y-%m-%d'),
            "textColor": "green" if row['margin_diff'] > 0 else "red",
            "className": "bg-white",
            "priority" : 1,
        })
        events.append({
            "title": f"IXIC RS: {round(row['margin_diff_pct'], 2)}% vs {round(row['^IXIC_diff_pct'], 2)}%",
            "start": row['date'].strftime('%Y-%m-%d'),
            "end": row['date'].strftime('%Y-%m-%d'),
            "textColor": "green" if float(row['margin_diff_pct']) > float(row['^IXIC_diff_pct'])
                                            else ("orange" if float(row['margin_diff_pct']) > 0 else "red"),
            "className": "bg-white",
            "priority": 2,
        })
        events.append({
            "title": f"{round(row['^IXIC_diff_pct'], 2)}% / {round(row['^DJI_diff_pct'], 2)}% / {round(row['^GSPC_diff_pct'], 2)}%",
            "start": row['date'].strftime('%Y-%m-%d'),
            "end": row['date'].strftime('%Y-%m-%d'),
            "textColor": "green" if row['^IXIC_diff'] > 0 else "red",
            "className": "bg-white",
            "priority": 3,
        })

    data = {
        "initialDate": initial_date,
        "events": events
    }
    return JsonResponse(data)


@csrf_exempt
def get_benchmark(request):

    # Step 0. Check input parameters
    user_id = request.user.id  # Assuming you have the user_id from the request
    portfolio = Portfolio.objects.filter(user=user_id, is_default=True).order_by('-portfolio_id').first()

    if not portfolio:
        return JsonResponse({'success': False, 'error': 'Default portfolio not found'}, status=404)

    as_of_date_str = request.GET.get('as_of_date')
    if not as_of_date_str:
        return JsonResponse({'success': False, 'error': 'as of date is not found'}, status=404)
    try:
        as_of_date = datetime.strptime(as_of_date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'success': False, 'error': 'Invalid date format'}, status=400)

    # Step 1. Main: Get the balance history
    data_df = instance.research.position().Portfolio().benchmark(portfolio, as_of_date)

    # Step 2. Extract: Prepare the data for the chart
    # Step 2.a chart
    labels = data_df['date'].astype(str).tolist()
    nasdaq_data = data_df['^IXIC_perf'].tolist()
    dow30_data = data_df['^DJI_perf'].tolist()
    sp500_data = data_df['^GSPC_perf'].tolist()
    margin_data = data_df['margin_perf'].tolist()

    # Step 2.b summary
    # Get the last row of data_df
    last_row = data_df.iloc[-1]
    # Calculate perf_pct
    perf_pct = round((last_row['margin_perf'] - 1) * 100, 2)

    data = {
        "summary": {
            "perf_pct": perf_pct
        },
        "data": {
            "labels": labels,
            "datasets": [{
                "label": "IXIC",
                "tension": 0,
                "pointRadius": 2,
                "pointBackgroundColor": "#cb0c9f",
                "borderColor": "#cb0c9f",
                "borderWidth": 3,
                "data": nasdaq_data,
                "maxBarThickness": 6
            }, {
                "label": "DJI",
                "tension": 0,
                "pointRadius": 2,
                "pointBackgroundColor": "#25b840",
                "borderColor": "#25b840",
                "borderWidth": 3,
                "data": dow30_data,
                "maxBarThickness": 6
            }, {
                "label": "GSPC",
                "tension": 0,
                "pointRadius": 2,
                "pointBackgroundColor": "#17c1e8",
                "borderColor": "#17c1e8",
                "borderWidth": 3,
                "data": sp500_data,
                "maxBarThickness": 6
            }, {
                "label": "portfolio",
                "tension": 0,
                "pointRadius": 2,
                "pointBackgroundColor": "#000000",
                "borderColor": "#000000",
                "borderWidth": 3,
                "data": margin_data,
                "maxBarThickness": 6
            }],
        }
    }

    return JsonResponse(data)

