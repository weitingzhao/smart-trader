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



        # # Check data readiness
        # market_symbol = MarketSymbol.objects.get(symbol=symbol)
        # if not market_symbol.daily_data_ready:
        #     return JsonResponse({'success': False, 'error': 'Daily data not ready'}, status=400)
        #
        # # Enable listen price Quote if needed
        # if not market_symbol.price_quote_enabled:
        #     market_symbol.enable_price_quote()

        # # Calculate indicators using backtrader
        # cerebro = bt.Cerebro()
        # # Add your data feed and strategy here
        # # cerebro.adddata(data)
        # # cerebro.addstrategy(MyStrategy)
        # cerebro.run()

        # # Calculate Stock ATR based on hist daily data
        # atr = calculate_atr(market_symbol.hist_data)
        #
        # # Calculate Bollinger bands and R/S using backtrader
        # bollinger_bands = calculate_bollinger_bands(market_symbol.hist_data)
        # rs_levels = calculate_rs_levels(market_symbol.hist_data)
        #
        # # Load band and R/S manual values
        # support_manual_low_price = market_symbol.support_manual_low_price
        # support_lv2_low_price = market_symbol.support_lv2_low_price
        # fix_1_percent_rate = calculate_fix_1_percent_rate(market_symbol)

        # Return all indicators to front page
        # return JsonResponse({
        #     'success': True,
        #     'order_section': {
        #         'atr': atr,
        #         'bollinger_bands': bollinger_bands,
        #         'rs_levels': rs_levels,
        #     },
        #     'sr_section': {
        #         'support_manual_low_price': support_manual_low_price,
        #         'support_lv2_low_price': support_lv2_low_price,
        #         'fix_1_percent_rate': fix_1_percent_rate,
        #     }
        # })
        return JsonResponse({'success': False, 'error': 'Symbol not found'}, status=404)
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