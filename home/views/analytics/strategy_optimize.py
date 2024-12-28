from django.shortcuts import render
from apps.common.models import *
from django.http import JsonResponse

from bokeh.client import pull_session
from bokeh.embed import server_session


def default(request):
    user_id = request.user.id  # Assuming you have the user_id from the request

    # Step 0. Get default portfolio
    portfolio = Portfolio.objects.filter(user=user_id, is_default=True).order_by('-portfolio_id').first()
    if not portfolio:
        return JsonResponse({'success': False, 'error': 'Default portfolio not found'}, status=404)



    session = pull_session(url="http://localhost:8092/")
    script = server_session(
        model=None,
        session_id = session.id,
        url = "http://localhost:8092/",
    )


    return render(
        request=request,
        template_name='pages/analytics/strategy_optimize.html',
        context= {
            'parent': 'analytics',
            'segment': 'strategy_optimize',
            'script': script,
        })