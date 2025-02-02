import json
import base64
from django.shortcuts import render
from apps.common.models import *
import business.logic as Logic
import home.templatetags.request_url as url
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

def default(request):

    user_id = request.user.id  # Assuming you have the user_id from the request
    portfolio = Portfolio.objects.filter(user=user_id, is_default=True).order_by('-portfolio_id').first()
    if not portfolio:
        return JsonResponse({'success': False, 'error': 'Default portfolio not found'}, status=404)


    wishlist_items = Wishlist.objects.all().order_by('order_position')

    return render(
        request=request,
        template_name='pages//screening/monitor.html',
        context={
            'parent': 'screening',
            'segment': 'monitor',
            'page_title': 'Live Monitor !!!',  # title
            'watchlist': wishlist_items
        })

@csrf_exempt
def strategy(request, strategy_id):
    try:
        user_id = request.user.id  # Assuming you have the user_id from the request
        portfolio = Portfolio.objects.filter(user=user_id, is_default=True).order_by('-portfolio_id').first()

        # Get the strategy based on the ref_strategy_id
        strategy = Strategy.objects.get(strategy_id=strategy_id)

        # Get the strategy based on the ref_strategy_id
        final_df = Logic.research().position().Close().Position(portfolio, strategy.strategy_id)
        summary = Logic.research().position().Close().summary(final_df)

        # Prepare the response data
        response_data = {
            'success': True,
            'strategy_id': strategy.strategy_id,
            'strategy_name': strategy.name,
            'summary': url.convert_to_serializable(summary),
        }

        return JsonResponse(response_data, status=200)
    except Wishlist.DoesNotExist:
        return JsonResponse({'error': 'Wishlist item not found'}, status=404)
    except Strategy.DoesNotExist:
        return JsonResponse({'error': 'Strategy not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def quote(request, symbol):
    try:
        # Get the wishlist record based on the symbol
        wishlist_item = Wishlist.objects.get(symbol_id=symbol)

        # Prepare the response data
        quote_data = {
            'success': True,
            'wishlist_id': wishlist_item.wishlist_id,
            'symbol_id': wishlist_item.symbol_id,

            'bollinger_upper': wishlist_item.bollinger_upper,
            'bollinger_lower': wishlist_item.bollinger_lower,
            'rs_upper_max': wishlist_item.rs_upper_max,
            'rs_upper_min': wishlist_item.rs_upper_min,
            'rs_lower_max': wishlist_item.rs_lower_max,
            'rs_lower_min': wishlist_item.rs_lower_min,
            'rs_upper_max_2': wishlist_item.rs_upper_max_2,
            'rs_upper_min_2': wishlist_item.rs_upper_min_2,
            'rs_lower_max_2': wishlist_item.rs_lower_max_2,
            'rs_lower_min_2': wishlist_item.rs_lower_min_2,

        }

        return JsonResponse(quote_data, status=200)
    except MarketSymbol.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Symbol not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
def portfolio(request):
    try:
        user_id = request.user.id  # Assuming you have the user_id from the request
        portfolio = Portfolio.objects.filter(user=user_id, is_default=True).order_by('-portfolio_id').first()

        if not portfolio:
            return JsonResponse({'error': 'Default portfolio not found'}, status=404)

        cash = portfolio.cash + portfolio.money_market
        # Get the UserStaticSetting based on the user_id
        user_static_setting = UserStaticSetting.objects.filter(user_id=user_id).first()

        open_final_df, max_date = Logic.research().position().Open().Position(portfolio)
        open_summary = Logic.research().position().Open().summary(portfolio, open_final_df)

        # Prepare the response data
        response_data = {
            'success': True,
            'capital' : open_summary['category']['total'],
            'available_cash': cash,
            'total_risk' : user_static_setting.risk,
            'single_max_drawdown': user_static_setting.single_max_drawdown,
        }

        return JsonResponse(response_data, status=200)
    except Wishlist.DoesNotExist:
        return JsonResponse({'error': 'Wishlist item not found'}, status=404)
    except Strategy.DoesNotExist:
        return JsonResponse({'error': 'Strategy not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)