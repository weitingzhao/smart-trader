from django.http import JsonResponse
from apps.common.models import *
from django.shortcuts import render
import business.logic as Logic


def default(request):
    user_id = request.user.id  # Assuming you have the user_id from the request
    portfolio = Portfolio.objects.filter(user=user_id, is_default=True).order_by('-portfolio_id').first()

    if not portfolio:
        return JsonResponse({'success': False, 'error': 'Default portfolio not found'}, status=404)

    ##### Calculate Open Position ##############
    final_df = Logic.research().position().Close().Position(portfolio)

    if final_df is None:
        summary = {}
        final_json = []
    else:
        ##### Calculate the summary tab ##############
        summary = Logic.research().position().Close().summary(final_df)
        # Convert the DataFrame to JSON
        final_json = final_df.to_json(orient='records', date_format='iso')

    return render(
        request = request,
        template_name='pages/position/close_positions.html',
        context= {
            'parent': 'position',
            'segment': 'close_positions',
            'portfolio': portfolio,
            'portfolio_items': final_json,
            'summary': summary,
            'page_title': 'Close Position'  # title
        })