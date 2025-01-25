import asyncio
import json
from django.http import JsonResponse
from django.shortcuts import render
from apps.common.models import Portfolio
from home.forms.portfolio import PortfolioForm
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt

from home.services.ib_quote_service import IntBrokersQuoteService
from home.services.price_quote_ws import StockPriceWS

def default(request):

    user_id = request.user
    # user_id = 2 # for testing user
    portfolios = Portfolio.objects.filter(user=user_id).order_by('-is_default')
    form = PortfolioForm()

    stock_price_live_socket_status = not IntBrokersQuoteService.is_instance_none()

    return render(
        request=request,
        template_name='pages/settings/account_settings.html',
        context={
            'parent': 'settings',
            'segment': 'account_settings',
            'portfolios': portfolios,
            'form': form,
            'stock_price_live_socket_status': stock_price_live_socket_status
        })

@csrf_exempt
def stock_live_price_ws(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        enabled = data.get('enabled', False)

        if enabled:
            # Create and connect the IB instance
            if IntBrokersQuoteService.is_instance_none():
                asyncio.run(IntBrokersQuoteService().start())
        else:
            # Disconnect and destroy the IB instance
            if not IntBrokersQuoteService.is_instance_none():
                asyncio.run(IntBrokersQuoteService().stop())

        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

@csrf_exempt
def add_portfolio(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            portfolio_name = data.get('name')

            if not portfolio_name:
                return JsonResponse({'success': False, 'error': 'Portfolio name is missing'}, status=400)

            user = request.user
            # user = User.objects.get(pk=2)

            portfolio = Portfolio.objects.create(name=portfolio_name, user=user)
            return JsonResponse({'success': True, 'portfolio_id': portfolio.pk})
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

@csrf_exempt
def edit_portfolio(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            portfolio_id = data.get('id')
            portfolio_name = data.get('name')

            if portfolio_id is None or not portfolio_name:
                return JsonResponse({'success': False, 'error': 'Invalid data'}, status=400)

            portfolio = Portfolio.objects.get(pk=portfolio_id)
            portfolio.name = portfolio_name
            portfolio.save()

            return JsonResponse({'success': True})
        except Portfolio.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Portfolio not found'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

@csrf_exempt
def toggle_default_portfolio(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            portfolio_id = data.get('id')
            is_default = data.get('is_default')

            if portfolio_id is None or is_default is None:
                return JsonResponse({'success': False, 'error': 'Invalid data'}, status=400)

            # Set all portfolios to is_default=False
            Portfolio.objects.filter(user=request.user).update(is_default=False)

            # Set the selected portfolio to is_default=True
            portfolio = Portfolio.objects.get(pk=portfolio_id)
            portfolio.is_default = is_default
            portfolio.save()

            return JsonResponse({'success': True})
        except Portfolio.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Portfolio not found'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

@csrf_exempt
def delete_portfolio(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            portfolio_id = data.get('id')

            if portfolio_id is None:
                return JsonResponse({'success': False, 'error': 'Invalid data'}, status=400)

            portfolio = Portfolio.objects.get(pk=portfolio_id)
            portfolio.delete()

            return JsonResponse({'success': True})
        except Portfolio.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Portfolio not found'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)



