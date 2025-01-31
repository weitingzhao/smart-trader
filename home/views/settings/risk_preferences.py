from django.shortcuts import render
from django.contrib import messages
import business.logic as Logic
from apps.common.models import *

def default(request):

    index = ['^IXIC', '^DJI', '^GSPC', 'NQ=F']

    # Get Portfolio Holding Symbols
    user_id = request.user.id  # Assuming you have the user_id from the request
    portfolio = Portfolio.objects.filter(user=user_id, is_default=True).order_by('-portfolio_id').first()
    if portfolio:
        holdings = Logic.research().position().Open().get_portfolio_holding(portfolio, index)
    else:
        holdings = []

    # Get All symbols
    all_symbols = list(Holding.objects.values_list('symbol', flat=True))
    all_symbols.extend(index)

    return render(
        request=request,
        template_name='pages/settings/risk_preferences.html',
        context= {
            'parent': 'settings',
            'segment': 'risk_preferences',
            'page_title': 'Risk Pre', # title
            'messages': messages.get_messages(request),
            'index': ','.join(index),
            'all_symbols': ','.join(all_symbols),
            'holdings': ','.join(holdings),
        })
































