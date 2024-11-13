import json
import pandas as pd
from decimal import Decimal
from datetime import datetime
from django.db.models import Sum, F
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from apps.common.models import *
from django.shortcuts import render, get_object_or_404

def get(request, transaction_id):
    transaction = get_object_or_404(Transaction, transaction_id=transaction_id)
    data = {
        'id': transaction.transaction_id,
        'quantity_final': transaction.quantity_final,
        'price_final': transaction.price_final,
        'date': transaction.date.strftime('%Y-%m-%d'),
        'commission': transaction.commission
    }
    return JsonResponse(data)

@csrf_exempt
def add(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        holding_id = data.get('holding_id')
        quantity_final = data.get('quantity_final')
        price_final = data.get('price_final')
        date = data.get('date') if data.get('date') != '' else datetime.now().strftime('%Y-%m-%d')
        commission = data.get('commission')

        reference = data.get('reference')
        # Update holding order with the new transaction_id based on reference
        if reference:
            ref_type = reference.get('type')
            ref_id = reference.get('ref_id')
            # Convert ref_type to integer using TransactionTypeChoices
            ref_type_int = TransactionTypeChoices[ref_type.upper()].value
            # Create new transaction
            transaction = Transaction.objects.create(
                transaction_type=ref_type_int,
                holding_id=holding_id,
                date=date,
                quantity_final=quantity_final,
                price_final=price_final,
                commission=commission
            )

            if ref_type == 'Buy':  # Buy
                transaction.buy_order_id = ref_id
            elif ref_type == 'Sell' :  # Sell
                transaction.sell_order_id = ref_id
            transaction.save()

            return JsonResponse({'status': 'success', 'transaction_id': transaction.transaction_id})

    return JsonResponse({'status': 'failed'}, status=400)

@csrf_exempt
def update(request, transaction_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        action = Transaction.objects.get(transaction_id=transaction_id)

        action.date = data.get('date')
        action.quantity_final = data.get('quantity_final') if data.get('quantity_final') != '' else None
        action.price_final = data.get('price_final') if data.get('price_final') != '' else None
        action.commission = data.get('commission') if data.get('commission') != '' else None
        action.save()
        return JsonResponse({'status': 'success', 'action': 'updated'})

    return JsonResponse({'status': 'failed'}, status=400)


@csrf_exempt
def delete(request, transaction_id):
    if request.method == 'DELETE':
        transaction = Transaction.objects.get(transaction_id=transaction_id)
        # Delete the transaction
        transaction.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'failed'}, status=400)