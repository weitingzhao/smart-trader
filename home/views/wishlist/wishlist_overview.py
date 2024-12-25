import math

from django.shortcuts import render
from django.utils import timezone

from apps.common.models import *
from apps.common.models import Wishlist
from apps.common.models import MarketSymbol
from logics.logic import Logic
from django.shortcuts import get_object_or_404
import pandas as pd
from pandas import DataFrame
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt

instance = Logic()


def default(request):

    user_id = request.user.id  # Assuming you have the user_id from the request
    portfolio = Portfolio.objects.filter(
        user=user_id, is_default=True).order_by('-portfolio_id').first()
    if not portfolio:
        return JsonResponse({'success': False, 'error': 'Default portfolio not found'}, status=404)

    return render(
        request=request,
        template_name='pages/wishlist/wishlist_overview.html',
        context={
            'parent': 'wishlist',
            'segment': 'wishlist_overview',
        })


@csrf_exempt
def add_wishlist(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            symbol = data.get('symbol')
            purpose = data.get('purpose')

            # target_buy_price = data.get('target_buy_price')
            # target_sell_stop = data.get('target_sell_stop')
            # target_sell_limit = data.get('target_sell_limit')
            # list_on = data.get('list_on')
            # is_filled = data.get('is_filled')
            # quantity= data.get('quantity')

            if not symbol:                
                return JsonResponse({'success': False, 'error': 'Portfolio name is missing'}, status=400)

            user = request.user

            symbol_martet= MarketSymbol.objects.get(pk=symbol)
            # user = User.objects.get(pk=2)

            try:
                portfolio = Wishlist.objects.create(
                    symbol=symbol_martet,
                    # quantity=quantity,
                    # target_buy_price=target_buy_price,
                    # target_sell_stop=target_sell_stop,
                    # is_filled=is_filled,
                    # target_sell_limit=target_sell_limit,
                    # list_on=list_on ,
                    add_by=user)
                return JsonResponse({'success': True, 'portfolio_id': portfolio.pk})
            except Exception as e:
                print(e.args)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)
