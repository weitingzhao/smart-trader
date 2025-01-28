from django.http import JsonResponse
from apps.common.models import *
from django.shortcuts import render
import business.logic as Logic

def default(request, strategy_id):
    user_id = request.user.id  # Assuming you have the user_id from the request
    portfolio = Portfolio.objects.filter(user=user_id, is_default=True).order_by('-portfolio_id').first()

    if not portfolio:
        return JsonResponse({'success': False, 'error': 'Default portfolio not found'}, status=404)

    ##### Calculate Open Position ##############
    final_df = Logic.research().position().Close().Position(portfolio, strategy_id)

    if final_df is None:
        summary = {}
        final_json = []
    else:
        ##### Calculate the summary tab ##############
        summary = Logic.research().position().Close().summary(final_df)
        # Convert the DataFrame to JSON
        final_json = final_df.to_json(orient='records', date_format='iso')

    # Query all records from the Strategy model
    trade_strategy = Logic.research().category().strategy().get_simple_dic()

    return render(
        request = request,
        template_name='pages/position/close_positions.html',
        context= {
            'parent': 'position',
            'segment': 'close_positions',
            'page_title': 'Close Position', # title
            'portfolio': portfolio,
            'portfolio_items': final_json,
            'strategy_id': strategy_id,
            'summary': summary,

            # Trade
            'trade_source_choices': TradeSourceChoices.choices,
            'trade_phase_choices': TradePhaseChoices.choices,
            'trade_phase_rating_choices': TradePhaseRatingChoices.choices,
            'trade_strategy': trade_strategy  # Add trade_strategy to context
        })