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

    ##### Calculate Open Position ##############
    final_df = instance.research.position().Close().Position(portfolio)

    if final_df is None:
        summary = {}
        final_json = []
    else:
        ##### Calculate the summary tab ##############
        summary = instance.research.position().Close().summary(final_df)
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
            'summary': summary,
            'page_title': 'Close Position'  # title
        })