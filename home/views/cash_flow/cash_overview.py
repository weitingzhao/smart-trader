import json
from apps.common.models.portfolio import Funding
from home.forms.portfolio import *
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404

def default(request):
    user_id = request.user.id  # Assuming you have the user_id from the request
    portfolio = Portfolio.objects.filter(user=user_id, is_default=True).order_by('-portfolio_id').first()

    if not portfolio:
        return JsonResponse({'success': False, 'error': 'Default portfolio not found'}, status=404)

    funding_data = Funding.objects.filter(portfolio=portfolio).order_by('-completion_date')
    cash_balance_data = CashBalance.objects.filter(portfolio=portfolio).order_by('-as_of_date')

    form_funding = FundingForm()
    form_cash_balance =  CashBalanceForm()

    return render(
        request=request,
        template_name='pages/cash_flow/cash_overview.html',
        context={
            'parent': 'cash_flow',
            'segment': 'cash_overview',
            'funding_data': funding_data,
            'cash_balance_data': cash_balance_data,
            'form_funding': form_funding,
            "form_cash_balance": form_cash_balance,
        }
    )

@csrf_exempt
def add_funding(request):
    user_id = request.user.id  # Assuming you have the user_id from the request
    portfolio = Portfolio.objects.filter(user=user_id, is_default=True).order_by('-portfolio_id').first()

    if request.method == 'POST':
        data = json.loads(request.body)
        completion_date = data.get('completion_date')
        funding_type = data.get('funding_type')
        amount = data.get('amount')

        if portfolio and completion_date and funding_type and amount:
            funding = Funding(
                portfolio=portfolio,
                completion_date=completion_date,
                funding_type=funding_type,
                amount=amount
            )
            funding.save()
            return JsonResponse({'status': 'success', 'funding_id': funding.funding_id})
    return JsonResponse({'status': 'failed'}, status=400)

def get_funding(request, funding_id):
    funding = get_object_or_404(Funding, funding_id=funding_id)
    data = {
        'funding_id': funding.funding_id,

        'funding_type': funding.funding_type,
        'amount': funding.amount,
        'completion_date': funding.completion_date,
    }
    return JsonResponse(data)

@csrf_exempt
def edit_funding(request, funding_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        funding = Funding.objects.get(funding_id=funding_id)

        funding.funding_type = data.get('funding_type')
        funding.amount = data.get('amount')
        funding.completion_date = data.get('completion_date')

        funding.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'failed'}, status=400)

@csrf_exempt
def delete_funding(request, funding_id):
    if request.method == 'DELETE':
        funding = Funding.objects.get(funding_id=funding_id)
        funding.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'failed'}, status=400)


@csrf_exempt
def add_cash_balance(request):
    user_id = request.user.id  # Assuming you have the user_id from the request
    portfolio = Portfolio.objects.filter(user=user_id, is_default=True).order_by('-portfolio_id').first()

    if request.method == 'POST':
        data = json.loads(request.body)
        as_of_date = data.get('as_of_date')
        money_market = data.get('money_market')
        cash = data.get('cash')

        if portfolio and as_of_date and money_market and cash:
            cash_balance = CashBalance(
                portfolio=portfolio,
                as_of_date=as_of_date,
                money_market=money_market,
                cash=cash
            )
            cash_balance.save()
            return JsonResponse({'status': 'success', 'cash_balance_id': cash_balance.cash_balance_id})
    return JsonResponse({'status': 'failed'}, status=400)

def get_cash_balance(request, balance_id):
    cash_balance = get_object_or_404(CashBalance, cash_balance_id=balance_id)
    data = {
        'cash_balance_id': cash_balance.cash_balance_id,

        'as_of_date': cash_balance.as_of_date,
        'money_market': cash_balance.money_market,
        'cash': cash_balance.cash
    }
    return JsonResponse(data)

@csrf_exempt
def edit_cash_balance(request, balance_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        cash_balance = CashBalance.objects.get(cash_balance_id=balance_id)

        cash_balance.as_of_date = data.get('as_of_date')
        cash_balance.money_market = data.get('money_market')
        cash_balance.cash = data.get('cash')

        cash_balance.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'failed'}, status=400)

@csrf_exempt
def delete_cash_balance(request, balance_id):
    if request.method == 'DELETE':
        cash_balance = CashBalance.objects.get(cash_balance_id=balance_id)
        cash_balance.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'failed'}, status=400)


