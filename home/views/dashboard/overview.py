import pandas as pd
from django.shortcuts import render
from apps.common.models import *
from django.http import JsonResponse

def default(request):

    user_id = request.user.id  # Assuming you have the user_id from the request

    # Step 0. Get default portfolio
    portfolio = Portfolio.objects.filter(user=user_id, is_default=True).order_by('-portfolio_id').first()
    if not portfolio:
        return JsonResponse({'success': False, 'error': 'Default portfolio not found'}, status=404)

    # Step 1. Get holdings under portfolio
    holdings = Holding.objects.filter(portfolio=portfolio)
    symbols = [item.symbol.symbol for item in holdings]
    if len(symbols) <= 0:
        return render(
            request= request, template_name='pages/dashboard/overview.html',
            context={ 'parent': 'dashboard', 'segment': 'overview', 'holdings': []})
    final_df = pd.DataFrame(list(holdings.values()))

    # Convert the DataFrame to JSON
    final_json = final_df.to_json(orient='records', date_format='iso')

    # Step 2. Get performance_tracking_date from UserStaticSetting
    user_static_setting = UserStaticSetting.objects.filter(user=user_id).first()
    perf_tracking_date = user_static_setting.performance_tracking_date if user_static_setting else None

    return render(
        request=request,
        template_name='pages/dashboard/overview.html',
        context= {
            'parent': 'dashboard',
            'segment': 'overview',
            'holdings': final_json,
            'perf_tracking_date': perf_tracking_date,
        })