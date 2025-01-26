import asyncio
import json
from django.http import JsonResponse
from django.shortcuts import render
from fontTools.varLib.plot import stops

from apps.common.models import Portfolio
from home.forms.portfolio import PortfolioForm
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt

from home.services.ib_quote_server import IntBrokersQuoteService
from home.services.price_quote_ws import StockQuoteWS
from home.services.tw_hist_sever import TradingViewHistService


def default(request):

    user_id = request.user
    # user_id = 2 # for testing user
    portfolios = Portfolio.objects.filter(user=user_id).order_by('-is_default')
    form = PortfolioForm()

    stock_live_price_service_status = IntBrokersQuoteService.is_exist()
    stock_hist_price_service_status = TradingViewHistService.is_exist()

    return render(
        request=request,
        template_name='pages/settings/account_settings.html',
        context={
            'parent': 'settings',
            'segment': 'account_settings',
            'portfolios': portfolios,
            'form': form,
            'stock_live_price_service_status': stock_live_price_service_status,
            'stock_hist_price_service_status': stock_hist_price_service_status
        })

@csrf_exempt
def stock_price(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        starting  = data.get('enabled', False)
        server = data.get('server', False)

        if server == 'quote':
            if starting :
                # Create and connect the IB instance
                if not IntBrokersQuoteService.is_exist():
                    asyncio.run(IntBrokersQuoteService().start())
            else:
                # Disconnect and destroy the IB instance
                if IntBrokersQuoteService.is_exist():
                    asyncio.run(IntBrokersQuoteService().stop())
        elif server == "hist":
            if starting:
                # Create and connect the IB instance
                if not TradingViewHistService.is_exist():
                    asyncio.run(TradingViewHistService().start())
            else:
                # Disconnect and destroy the IB instance
                if TradingViewHistService.is_exist():
                    asyncio.run(TradingViewHistService().stop())

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



