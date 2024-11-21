from django.shortcuts import render
import json
from apps.common.models.portfolio import Funding
from home.forms.portfolio import *
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404
from django.db.models import F, ExpressionWrapper, FloatField,Case, When, Value
from django.db.models.functions import Coalesce

def default(request):

    user_id = request.user.id  # Assuming you have the user_id from the request
    portfolio = Portfolio.objects.filter(user=user_id, is_default=True).order_by('-portfolio_id').first()

    if not portfolio:
        return JsonResponse({'success': False, 'error': 'Default portfolio not found'}, status=404)

    holdings = Holding.objects.filter(portfolio=portfolio)
    if len(holdings) <= 0:
        return None,None

    # Query transactions based on holdings ordered by date
    transaction_data = Transaction.objects.filter(holding__in=holdings).select_related('holding').annotate(
        amount=ExpressionWrapper(
            F('quantity_final') * F('price_final') +  Coalesce(F('commission'), Value(0)),
            output_field=FloatField()
        ),
        trade_id=Case(
            When(buy_order_id__isnull=False, then=F('buy_order__trade_id')),
            When(sell_order_id__isnull=False, then=F('sell_order__trade_id')),
            default=Value(None),
            output_field=FloatField()
        )
    ).order_by('-date')

    # Query holding_sell_order ordered by order_place_date desc and include symbol_id
    holding_sell_orders = HoldingSellOrder.objects.filter(holding__in=holdings).select_related('holding').annotate(
        symbol_id=F('holding__symbol_id')
    ).order_by('-order_place_date')

    # Query holding_buy_order ordered by holding_buy_order_id desc and include symbol_id
    holding_buy_orders = HoldingBuyOrder.objects.filter(holding__in=holdings).select_related('holding').annotate(
        symbol_id=F('holding__symbol_id')
    ).order_by('-holding_buy_order_id')

    return render(
        request=request,
        template_name='pages/performance/trade_history.html',
        context={
            'parent': 'performance',
            'segment': 'trade_history',
            'transaction_data': transaction_data,
            'holding_sell_orders': holding_sell_orders,
            'holding_buy_orders': holding_buy_orders,
        }
    )
