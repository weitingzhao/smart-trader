import math

from django.shortcuts import render
from django.utils import timezone

from apps.common.models import *
from logics.logic import Logic
from django.shortcuts import get_object_or_404
import pandas as pd
from pandas import DataFrame
from django.http import JsonResponse

instance = Logic()

def default(request):

    user_id = request.user.id  # Assuming you have the user_id from the request
    portfolio = Portfolio.objects.filter(user=user_id, is_default=True).order_by('-portfolio_id').first()
    if not portfolio:
        return JsonResponse({'success': False, 'error': 'Default portfolio not found'}, status=404)

    return render(
        request=request,
        template_name='pages/wishlist/wishlist_overview.html',
        context= {
            'parent': 'wishlist',
            'segment': 'wishlist_overview',
        })


