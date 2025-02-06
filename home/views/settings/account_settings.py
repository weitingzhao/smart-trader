import asyncio
import json
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from apps.common.models import *
from home.forms.portfolio import PortfolioForm
from django.views.decorators.csrf import csrf_exempt
from home.forms.portfolio import UserStaticSettingForm
from home.services.bt_trading_server import BTTradingService
from home.services.ib_quote_server import IBPriceQuoteService
from home.services.tw_hist_sever import TWPriceHistService


def default(request):

    user_id = request.user
    # user_id = 2 # for testing user
    portfolios = Portfolio.objects.filter(user=user_id).order_by('-is_default')
    if not portfolio:
        return JsonResponse({'success': False, 'error': 'Default portfolio not found'}, status=404)

    try:
        user_static_setting = UserStaticSetting.objects.get(user=request.user)
        form_static_risk = UserStaticSettingForm(instance=user_static_setting)
    except UserStaticSetting.DoesNotExist:
        form_static_risk = UserStaticSettingForm()

    portfolio_form = PortfolioForm()

    stock_live_trading_service_status = BTTradingService.is_exist()
    stock_live_price_service_status = IBPriceQuoteService.is_exist()
    stock_hist_price_service_status = TWPriceHistService.is_exist()

    return render(
        request=request,
        template_name='pages/settings/account_settings.html',
        context={
            'parent': 'settings',
            'segment': 'account_settings',
            'page_title': 'Account settings',  # title
            'portfolios': portfolios,
            'form': portfolio_form,
            'static_risk_form': form_static_risk,
            'stock_live_trading_service_status': stock_live_trading_service_status,
            'stock_live_price_service_status': stock_live_price_service_status,
            'stock_hist_price_service_status': stock_hist_price_service_status
        })

@csrf_exempt
def static_risk(request):
    if request.method == 'POST':
        form = UserStaticSettingForm(request.POST)
        if form.is_valid():
            position_sizing, created = UserStaticSetting.objects.update_or_create(
                user=request.user,
                defaults=form.cleaned_data
            )
            if created:
                messages.success(request, 'static risk created successfully.', extra_tags='static risk')
            else:
                messages.success(request, 'static risk updated successfully.', extra_tags='static risk')
        else:
            messages.error(request, f'static risk form is invalid.', extra_tags='static risk')
            return redirect('account_settings')
    else:
        messages.error(request, "method not supported", extra_tags='position sizing')
    return redirect('account_settings')

@csrf_exempt
def stock_price(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        starting  = data.get('enabled', False)
        server = data.get('server', False)

        if server == "trading":
            if starting :
                # Create and connect the Back Trader instance
                if not BTTradingService.is_exist():
                    asyncio.run(BTTradingService().start())
            else:
                # Disconnect and destroy the Back Trader  instance
                if BTTradingService.is_exist():
                    asyncio.run(BTTradingService().stop())
        elif server == 'quote':
            if starting :
                # Create and connect the IB instance
                if not IBPriceQuoteService.is_exist():
                    asyncio.run(IBPriceQuoteService().start())
            else:
                # Disconnect and destroy the IB instance
                if IBPriceQuoteService.is_exist():
                    asyncio.run(IBPriceQuoteService().stop())
        elif server == "hist":
            if starting:
                # Create and connect the IB instance
                if not TWPriceHistService.is_exist():
                    asyncio.run(TWPriceHistService().start())
            else:
                # Disconnect and destroy the IB instance
                if TWPriceHistService.is_exist():
                    asyncio.run(TWPriceHistService().stop())

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



