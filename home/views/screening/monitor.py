from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import render
from apps.common.models import *
import business.logic as Logic
import home.templatetags.request_url as url

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
def risk(request, symbol):
    try:
        user_id = request.user.id  # Assuming you have the user_id from the request
        portfolio = Portfolio.objects.filter(user=user_id, is_default=True).order_by('-portfolio_id').first()

        # Get the wishlist record based on the symbol
        wishlist_item = Wishlist.objects.get(symbol=symbol)
        # Get the strategy based on the ref_strategy_id
        strategy = Strategy.objects.get(strategy_id=wishlist_item.ref_strategy_id)

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
def sizing(request, symbol):
    pass

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