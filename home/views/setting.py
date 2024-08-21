from django.urls import reverse
from django.http import JsonResponse
from django.shortcuts import render, redirect
from home.base_home import BaseHome
from apps.notifications.signals import notify
from logic.engines.notify_engine import Level

# Create your views here.
instance = BaseHome()

# Pages -> Accounts
def settings(request):
    return render(
        request,
        template_name='pages/account/settings.html',
        context = {
            'parent': 'dashboard',
            'segment': 'settings'
        })


def fetching_company_info(request):
    if request.method != 'GET':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})

    # instance.service.fetching().symbol().fetch_symbols_info()

    # company_view = instance.service.fetching().symbol().fetch_symbols_info()
    # notify.send(user, recipient=user, verb='you reached level 10')
    # notify.send(actor, recipient, verb, action_object, target, level, description, public, timestamp, **kwargs)
    # post_save.connect(my_handler, sender=MyModel)
    # Example notification
    # action_object = MarketSymbol.objects.get(symbol__exact='AAPL')
    # target = MarketSymbol.objects.get(symbol__exact='UI')

    return instance.engine.notify(request.user).send(
        recipient=request.user,
        verb='Start fetching company info task',
        # #optional
        level=Level.INFO,
        description='fetched company info at backend, goto task page to see the progress',
    )

def fetching_symbol(request):
    if request.method == 'POST':
        instance.service.fetching().symbol().fetching_symbol()
        return redirect(reverse('stock screener') + '?status_message=All Market Symbol updated successfully')
    return redirect('stock screener')

def indexing_symbol(request):
    if request.method == "POST":
        instance.service.saving().symbol().index_symbol()
        return redirect(reverse('stock screener') + '?status_message=Market symbols indexed successfully')
    return redirect('stock screener')


def my_handler(sender, instance, created, **kwargs):
    notify.send(instance, verb='was saved')

