from django.shortcuts import render, redirect

from home.forms.portfolio import *


def default(request):
    user = request.user
    portfolio = Portfolio.objects.filter(user=user, is_default=True).order_by('-portfolio_id').first()
    holdings = Holding.objects.filter(portfolio_id=portfolio.portfolio_id)

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # get Market Symbol
            holding_symbol = form.cleaned_data['holding_symbol']
            market_symbol = MarketSymbol.objects.get(symbol=holding_symbol)

            # create or get Holding model base on market_symbol
            holding, created = Holding.objects.get_or_create(symbol=market_symbol, portfolio_id=portfolio.portfolio_id)

            # create buy order base on holding
            holding_buy_order = form.save(commit=False)
            holding_buy_order.holding = holding
            holding_buy_order.save()

            form.save()
            return redirect('initial_positions')  # Replace with your success URL
    else:
        form = OrderForm()

    return render(request,
        template_name='pages/wishlist/initial_positions.html',
        context={
            'form': form,
            'portfolio': portfolio,
            'holdings': holdings,
            'parent': 'wishlist',
            'segment': 'initial_positions',
        })

