from django.shortcuts import render
from apps.common.models import *
from django.http import JsonResponse


def default(request):

    user_id = request.user.id  # Assuming you have the user_id from the request
    portfolio = Portfolio.objects.filter(
        user=user_id, is_default=True).order_by('-portfolio_id').first()
    if not portfolio:
        return JsonResponse({'success': False, 'error': 'Default portfolio not found'}, status=404)




    return render(
        request=request,
        template_name='pages//screening/monitor.html',
        context={
            'parent': 'screening',
            'segment': 'monitor',
        })


