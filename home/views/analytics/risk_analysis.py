

from numpy.f2py.crackfortran import analyzeargs

from logics.logic import Logic
from django.shortcuts import render
from apps.common.models import *
from django.http import JsonResponse
from apps.tasks.controller import Cerebro_task as cerebro

instance = Logic()



def default(request, symbol, cut_over):
    user_id = request.user.id  # Assuming you have the user_id from the request

    # Step 0. Get default portfolio
    portfolio = Portfolio.objects.filter(user=user_id, is_default=True).order_by('-portfolio_id').first()
    if not portfolio:
        return JsonResponse({'success': False, 'error': 'Default portfolio not found'}, status=404)

    if not symbol:
        return JsonResponse({'success': False, 'error': 'Symbol not provided'}, status=400)

    analysis_result, plot  =  cerebro.run_cerebro_strategy(symbol, cut_over)

    # cerebro.opt_cerebro_strategy(symbol, cut_over)


    return render(
        request=request,
        template_name='pages/analytics/risk_analysis.html',
        context= {
            'parent': 'analytics',
            'segment': 'risk_analysis',
            'analysis_result': analysis_result,
            'plot': plot
        })
