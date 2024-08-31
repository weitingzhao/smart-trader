from django.shortcuts import render, get_object_or_404, redirect

from home.forms.portfolio import PortfolioForm, PortfolioItemForm
from home.models.portfolio import Portfolio, PortfolioItem, Transaction


def portfolio_list(request):
    # user_id = request.user
    user_id = 2 # for testing user
    portfolios = Portfolio.objects.filter(user=user_id)
    return render(request, 'pages/portfolio/portfolio_list.html', {
        'parent': 'portfolio',
        'segment': 'my portfolio',
        'portfolios': portfolios
    })

def portfolio_detail(request, pk):
    portfolio = get_object_or_404(Portfolio, pk=pk)
    items = PortfolioItem.objects.filter(portfolio=portfolio)
    return render(request, 'pages/portfolio/portfolio_detail.html', {'portfolio': portfolio, 'items': items})

def add_portfolio(request):
    if request.method == 'POST':
        form = PortfolioForm(request.POST)
        if form.is_valid():
            portfolio = form.save(commit=False)
            portfolio.user = request.user
            portfolio.save()
            return redirect('portfolio_list')
    else:
        form = PortfolioForm()
    return render(request, 'pages/portfolio/add_portfolio.html', {'form': form})

def add_portfolio_item(request, pk):
    portfolio = get_object_or_404(Portfolio, pk=pk)
    if request.method == 'POST':
        form = PortfolioItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.portfolio = portfolio
            item.save()
            return redirect('portfolio_detail', pk=pk)
    else:
        form = PortfolioItemForm()
    return render(request, 'pages/portfolio/add_portfolio_item.html', {'form': form, 'portfolio': portfolio})

def transaction_history(request, pk):
    item = get_object_or_404(PortfolioItem, pk=pk)
    transactions = Transaction.objects.filter(portfolio_item=item)
    return render(request, 'pages/portfolio/transaction_history.html', {'item': item, 'transactions': transactions})


