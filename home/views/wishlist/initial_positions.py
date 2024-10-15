from django.shortcuts import render, redirect

from home.forms.portfolio import *


def default(request):
    user = request.user
    portfolio = Portfolio.objects.filter(user=user, is_default=True).order_by('-portfolio_id').first()

    if request.method == 'POST':
        form = HoldingBuyOrderForm(request.POST)
        if form.is_valid():
            # get or create Holding model
            holding_symbol = form.cleaned_data['holding_symbol']
            holding, created = Holding.objects.get_or_create(symbol=holding_symbol, portfolio_id=portfolio.portfolio_id)

            holding_buy_order = form.save(commit=False)
            holding_buy_order.holding = holding
            holding_buy_order.save()

            form.save()
            return redirect('initial_positions')  # Replace with your success URL
    else:
        form = HoldingBuyOrderForm()

    return render(request,
        template_name='pages/wishlist/initial_positions.html',
        context={
            'form': form,
            'portfolio': portfolio,
            'parent': 'wishlist',
            'segment': 'initial_positions',
        })

