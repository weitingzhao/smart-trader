from django.shortcuts import render, redirect
from django.contrib import messages
from home.forms.portfolio import *



def default(request):
    user = request.user
    portfolio = Portfolio.objects.filter(user=user, is_default=True).order_by('-portfolio_id').first()
    holdings = Holding.objects.filter(portfolio_id=portfolio.portfolio_id)

    if request.method == 'POST':
        form = HoldingSellOrderForm(request.POST)
        if form.is_valid():
            try:
                # get Market Symbol
                holding_symbol = form.cleaned_data['holding_symbol']
                market_symbol = MarketSymbol.objects.get(symbol=holding_symbol)

                # get Holding model base on market_symbol
                holding = Holding.objects.get(symbol=market_symbol, portfolio_id=portfolio.portfolio_id)

                # create buy order base on holding
                holding_buy_order = form.save(commit=False)
                holding_buy_order.holding = holding
                holding_buy_order.save()

                form.save()
                return redirect('initial_positions')  # Replace with your success URL
            except (MarketSymbol.DoesNotExist, Holding.DoesNotExist):
                messages.warning(request, 'The specified holding does not exist.')
                return redirect('adjust_stop_limits')  # Replace with your form URL
        else:
            # Handle form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error in {field}: {error}")
    else:
        form = HoldingSellOrderForm()

    return render(
        request=request,
        template_name='pages/position/adjust_stop_limits.html',
        context= {
            'form': form,
            'portfolio': portfolio,
            'holdings': holdings,
            'parent': 'position',
            'segment': 'adjust_stop_limits',
        })
