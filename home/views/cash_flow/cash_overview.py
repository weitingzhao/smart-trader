import json
from apps.common.models.portfolio import Funding
from home.forms.portfolio import *
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404

def default(request):
    funding_data = Funding.objects.all()

    form_funding = FundingForm()

    return render(
        request=request,
        template_name='pages/cash_flow/cash_overview.html',
        context={
            'parent': 'cash_flow',
            'segment': 'cash_overview',
            'funding_data': funding_data,
            'form_funding': form_funding
        }
    )

@csrf_exempt
def add(request):
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

