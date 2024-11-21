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

    user_id = request.user.id  # Assuming you have the user_id from the request
    portfolio = Portfolio.objects.filter(user=user_id, is_default=True).order_by('-portfolio_id').first()

    if not portfolio:
        return JsonResponse({'success': False, 'error': 'Default portfolio not found'}, status=404)

    balance_df = instance.research.position().Portfolio().balance_history(portfolio)

    # Last Step: Prepare the data for the chart
    labels = balance_df['date'].astype(str).tolist()

    market_data = balance_df['total_market'].tolist()
    asset_data = balance_df['total_asset'].tolist()
    invest_data = balance_df['total_invest'].tolist()

    chart_data = {
        "labels": labels,
        "datasets": [{
            "label": "market",
            "tension": 0,
            "pointRadius": 0,
            "borderColor": "#cb0c9f",
            "borderWidth": 3,
            "fill": True,
            "data": market_data,
            "maxBarThickness": 6
        }, {
            "label": "assets",
            "tension": 0,
            "pointRadius": 0,
            "borderColor": "#3A416F",
            "borderWidth": 3,
            "fill": True,
            "data": asset_data,
            "maxBarThickness": 6
        }, {
            "label": "invest",
            "tension": 0,
            "pointRadius": 0,
            "borderColor": "#16ce38",
            "borderWidth": 3,
            "fill": True,
            "data": invest_data,
            "maxBarThickness": 6
        }],
    }
    return JsonResponse(chart_data)

@csrf_exempt
def get_balance_calendar(request):

    user_id = request.user.id  # Assuming you have the user_id from the request
    portfolio = Portfolio.objects.filter(user=user_id, is_default=True).order_by('-portfolio_id').first()

    if not portfolio:
        return JsonResponse({'success': False, 'error': 'Default portfolio not found'}, status=404)

    balance_df = instance.research.position().Portfolio().balance_calendar(portfolio)

    # Get the minimum date from balance_df
    initial_date = datetime.today().replace(day=1).strftime('%Y-%m-%d')

    # Create events based on balance_df
    events = []
    for _, row in balance_df.iterrows():
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

    json_data = {
        "initialDate": initial_date,
        "events": events
    }

    return JsonResponse(json_data)


