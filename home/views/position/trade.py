import json
import pandas as pd
from decimal import Decimal
from datetime import datetime
from django.db.models import Sum, F
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from apps.common.models import *
from django.shortcuts import render, get_object_or_404

from home.views import position


@csrf_exempt
def update_phase(request, trade_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        trade_phase = data.get('trade_phase')

        try:
            trade = Trade.objects.get(trade_id=trade_id)
            trade.trade_phase = trade_phase
            trade.save()
            return JsonResponse({'status': 'success', 'action': 'updated'})
        except Trade.DoesNotExist:
            return JsonResponse({'status': 'failed', 'error': 'Trade not found'}, status=404)

    return JsonResponse({'status': 'failed'}, status=400)