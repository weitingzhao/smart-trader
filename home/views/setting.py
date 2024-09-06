from datetime import datetime

from django.db import connection
from django.http import JsonResponse
from django.shortcuts import render, redirect
from logic.logic import Logic
from apps.notifications.signals import notify
from apps.tasks import tasks

# Create your views here.
instance = Logic()

# Pages -> Accounts

def get_market_summary():
    queries = [
        "SELECT COUNT(*) FROM market_stock_hist_bars_min_ts",
        "SELECT COUNT(*) FROM market_stock_hist_bars_day_ts",
        "SELECT COUNT(*) FROM market_symbol",
        "SELECT COUNT(*) FROM market_stock",
        "SELECT COUNT(*) FROM market_company_officer",
        "SELECT COUNT(*) FROM market_stock_dividend",
        "SELECT COUNT(*) FROM market_stock_financial",
        "SELECT COUNT(*) FROM market_stock_performance",
        "SELECT COUNT(*) FROM market_stock_price",
        "SELECT COUNT(*) FROM market_stock_risk_metrics",
        "SELECT COUNT(*) FROM market_stock_share",
        "SELECT COUNT(*) FROM market_stock_target",
        "SELECT COUNT(*) FROM market_stock_valuation"
    ]

    counts = {}
    with connection.cursor() as cursor:
        for query in queries:
            cursor.execute(query)
            table_name = query.split(" ")[3]
            counts[table_name] = cursor.fetchone()[0]
    return counts


def settings(request):
    return render(
        request,
        template_name='pages/account/settings.html',
        context = {
            'parent': 'tools',
            'segment': 'settings',
            'counts': get_market_summary()
        })

def customize(request):
    return render(
        request,
        template_name='pages/account/customize.html',
        context = {
            'parent': 'account',
            'segment': 'customize',
            'counts': get_market_summary()
        })

def celery_task(request, task_name, args):
    if request.method != 'GET':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})

    try:
        feedback = tasks.backend_task.delay({
            'user_id': request.user.id,
            'task_name': task_name,
            'args': args,
        })
        return JsonResponse({
            'success': True,
            'on': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status': feedback.status,
            'task_id': feedback.task_id})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def my_handler(sender, instance, created, **kwargs):
    notify.send(instance, verb='was saved')

