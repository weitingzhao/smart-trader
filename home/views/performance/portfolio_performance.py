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
            "tension": 0.4,
            "pointRadius": 0,
            "borderColor": "#cb0c9f",
            "borderWidth": 3,
            "fill": True,
            "data": market_data,
            "maxBarThickness": 6
        }, {
            "label": "assets",
            "tension": 0.4,
            "pointRadius": 0,
            "borderColor": "#3A416F",
            "borderWidth": 3,
            "fill": True,
            "data": asset_data,
            "maxBarThickness": 6
        }, {
            "label": "invest",
            "tension": 0.4,
            "pointRadius": 0,
            "borderColor": "#16ce38",
            "borderWidth": 3,
            "fill": True,
            "data": invest_data,
            "maxBarThickness": 6
        }],
    }
    return JsonResponse(chart_data)


