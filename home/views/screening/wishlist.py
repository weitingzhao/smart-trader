import pandas as pd
import numpy as np
import decimal
import json
from django.core.paginator import Paginator
from django.shortcuts import render
from apps.common.models import *
from apps.common.models import Wishlist
from apps.common.models import MarketSymbol
from django.http import JsonResponse

from django.views.decorators.csrf import csrf_exempt
import business.logic as Logic


def default(request):

    user_id = request.user.id  # Assuming you have the user_id from the request
    portfolio = Portfolio.objects.filter(
        user=user_id, is_default=True).order_by('-portfolio_id').first()
    if not portfolio:
        return JsonResponse({'success': False, 'error': 'Default portfolio not found'}, status=404)

    # Query all records from the Strategy model
    trade_strategy = Logic.research().category().strategy().get_simple_dic(need_uncategorized=False)


    return render(
        request=request,
        template_name='pages//screening/wishlist.html',
        context={
            'parent': 'screening',
            'segment': 'wishlist',
            'trade_strategy': trade_strategy  # Add trade_strategy to context
        })

@csrf_exempt
def order_wishlist(request, direction: str):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

    try:
        data = json.loads(request.body)
        symbol_id = data.get('symbol_id')

        if not symbol_id:
            return JsonResponse({'success': False, 'error': 'Symbol ID is missing'}, status=400)

        wishlist_item = Wishlist.objects.get(symbol_id=symbol_id)
        current_order = wishlist_item.order_position

        if direction == 'up':
            new_order = current_order - 1
        elif direction == 'down':
            new_order = current_order + 1
        else:
            return JsonResponse({'success': False, 'error': 'Invalid direction'}, status=400)

        # Swap orders with the adjacent item
        adjacent_item = Wishlist.objects.filter(order_position=new_order).first()
        if adjacent_item:
            adjacent_item.order_position = current_order
            adjacent_item.save()

        wishlist_item.order_position = new_order
        wishlist_item.save()

        return JsonResponse({'success': True})
    except Wishlist.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Wishlist item not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
def get_wishlist(request, symbol):
    try:
        wishlist_item = Wishlist.objects.get(symbol=symbol)
        data = {
            'symbol': wishlist_item.symbol.pk,
            'trade_strategy': wishlist_item.ref_strategy.pk if wishlist_item.ref_strategy else None,
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
        return JsonResponse({'success': True, 'wishlist': data})
    except Wishlist.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Wishlist item not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
def add_wishlist(request):

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

    try:
        data = json.loads(request.body)
        symbol_id = data.get('symbol')

        if not symbol_id:
            return JsonResponse({'success': False, 'error': 'Portfolio name is missing'}, status=400)

        user = request.user
        symbol = MarketSymbol.objects.get(pk=symbol_id)
        # user = User.objects.get(pk=2)

        strategy_id = data.get('trade_strategy')
        strategy = None
        if strategy_id:
            strategy = Strategy.objects.get(strategy_id=strategy_id)


        wishlist, created = Wishlist.objects.update_or_create(
            symbol=symbol,
            defaults={
                'ref_strategy': strategy,
                'add_by': user
            }
        )

        if created:
            max_order_position = Wishlist.objects.aggregate(max_order=models.Max('order_position'))['max_order']
            wishlist.order_position = (max_order_position or 0) + 1
            wishlist.save()

        return JsonResponse({'success': True, 'wishlist_id': wishlist.pk, 'created': created})
    except Exception as e:
        print(e.args)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

@csrf_exempt
def update_wishlist(request):

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

    try:
        data = json.loads(request.body)
        symbol_id = data.get('symbol')

        if not symbol_id:
            return JsonResponse({'success': False, 'error': 'Portfolio name is missing'}, status=400)

        user = request.user
        symbol = MarketSymbol.objects.get(pk=symbol_id)
        # user = User.objects.get(pk=2)

        strategy_id = data.get('trade_strategy')
        strategy = None
        if strategy_id:
            strategy = Strategy.objects.get(strategy_id=strategy_id)

        def get_value_or_none(value):
            return value if value != "" else None

        wishlist, created = Wishlist.objects.update_or_create(
            symbol=symbol,
            defaults={
                'ref_strategy': strategy,
                'bollinger_upper': get_value_or_none(data.get('bollinger_upper')),
                'bollinger_lower': get_value_or_none(data.get('bollinger_lower')),
                'rs_upper_max': get_value_or_none(data.get('rs_upper_max')),
                'rs_upper_min': get_value_or_none(data.get('rs_upper_min')),
                'rs_lower_max': get_value_or_none(data.get('rs_lower_max')),
                'rs_lower_min': get_value_or_none(data.get('rs_lower_min')),
                'rs_upper_max_2': get_value_or_none(data.get('rs_upper_max_2')),
                'rs_upper_min_2': get_value_or_none(data.get('rs_upper_min_2')),
                'rs_lower_max_2': get_value_or_none(data.get('rs_lower_max_2')),
                'rs_lower_min_2': get_value_or_none(data.get('rs_lower_min_2')),
                'add_by': user
            }
        )

        if created:
            max_order_position = Wishlist.objects.aggregate(max_order=models.Max('order_position'))['max_order']
            wishlist.order_position = (max_order_position or 0) + 1
            wishlist.save()

        return JsonResponse({'success': True, 'wishlist_id': wishlist.pk, 'created': created})
    except Exception as e:
        print(e.args)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)


@csrf_exempt
def fetching(request):

    # Pagination parameters
    page_size = int(request.GET.get('pageSize'))
    page_number = int(request.GET.get('page', 1))
    # Where parameters
    search_value = request.GET.get('keywords')
    search_column = "sd.symbol_id"
    # Order parameters
    sort_default_column = " sd.symbol_id"
    sort_column = request.GET.get('sortColumn')
    sort_direction = request.GET.get('sortDirection')


    # Step 1. Prepare summary query script
    def summary_query() -> str:
        return f"""
        SELECT
            w.symbol_id
             , s.strategy_id
             , s.name
             , s.description
             , w.order_position
         FROM
             wishlist w
             LEFT JOIN strategy s ON w.ref_strategy_id = s.strategy_id
        ORDER BY w.order_position DESC
        """

    # Step 1.a Count Sql
    count_sql = f"""
        WITH summary AS ( {summary_query()})
        , count AS (SELECT symbol_id FROM summary  GROUP BY symbol_id)
    """
    # print(count_sql)

    # Step 1.b Main Sql
    main_sql = f"""
    WITH result AS (
        {summary_query()}
    )
    SELECT
        ROW_NUMBER() OVER (ORDER BY sd.order_position) AS row_num,
        *
    FROM
        result sd    
    """
    # print(data_query)

    return JsonResponse(Logic.engine().sql_alchemy().query_pagination(
        count_sql=count_sql, main_sql=main_sql,
        search_column=search_column, search_value=search_value,
        sort_default_column=sort_default_column, sort_column=sort_column, sort_direction=sort_direction,
        page_size=page_size, page_number= page_number))


@csrf_exempt
def delete_wishlist(request, symbol: str):
    if request.method == 'DELETE':
        try:
            wishlist_item = Wishlist.objects.get(symbol=symbol)
            wishlist_item.delete()

            # Recalculate order_position for remaining items
            remaining_items = Wishlist.objects.all().order_by('order_position')
            for index, item in enumerate(remaining_items):
                item.order_position = index + 1
                item.save()

            return JsonResponse({'success': True})
        except Wishlist.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Wishlist item not found'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)