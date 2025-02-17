from django.shortcuts import render, redirect

from home.forms.portfolio import *


def default(request):
    user = request.user
    portfolio = Portfolio.objects.filter(user=user, is_default=True).order_by('-portfolio_id').first()
    holdings = Holding.objects.filter(portfolio_id=portfolio.portfolio_id)

    if request.method == 'POST':
        # get Market Symbol
        holding_symbol = request.POST.get('holding_symbol')
        market_symbol = MarketSymbol.objects.get(symbol=holding_symbol)

        # create or get Holding model base on market_symbol
        holding, created = Holding.objects.get_or_create(symbol=market_symbol, portfolio_id=portfolio.portfolio_id)

        # create buy order base on holding
        # holding_buy_order = form.save(commit=False)
        # holding_buy_order.holding = holding
        # holding_buy_order.save()
        return redirect('initial_positions')  # Replace with your success URL

    return render(request,
                  template_name='pages/screening/initial_positions.html',
                  context={
            'portfolio': portfolio,
            'holdings': holdings,
            'parent': 'screening',
            'segment': 'initial_positions',
            'page_title': 'Initial Holding'  # title
        })

