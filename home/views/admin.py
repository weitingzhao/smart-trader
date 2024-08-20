import uuid
from datetime import timedelta
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone

from home.base_home import BaseHome
from django.db.models.signals import post_save
from apps.notifications.signals import notify

from home.models import MarketSymbol

# Create your views here.
instance = BaseHome()

# Pages -> Accounts
def settings(request):
  context = {
    'parent': 'dashboard',
    'sub_parent': 'accounts',
    'segment': 'settings'
  }
  return render(request, 'pages/account/settings.html', context)

def settings_fetching_company_info(request):
    if request.method != 'GET':
      return JsonResponse({'success': False, 'error': 'Invalid request method'})
    try:
        # company_view = instance.service.fetching().symbol().fetch_symbols_info()

        # notify.send(user, recipient=user, verb='you reached level 10')
        # notify.send(actor, recipient, verb, action_object, target, level, description, public, timestamp, **kwargs)
        # post_save.connect(my_handler, sender=MyModel)
        # Example notification

        action_object = MarketSymbol.objects.get(symbol__exact='AAPL')
        target = MarketSymbol.objects.get(symbol__exact='UI')

        notify.send(
            sender=request.user,
            recipient=request.user,
            verb='fetched fundamental company info2',
            # #optional
            data="you got it",
            action_object=action_object,
            target=target,
            level='error', #success, info, warning, error
            description='description : fetched fundamental company info',
            public=True,
            timestamp=timezone.now() - timedelta(hours=15)
        )

        return JsonResponse({'success': True, 'data': "\r\n".join(["line1","line2"])})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def my_handler(sender, instance, created, **kwargs):
    notify.send(instance, verb='was saved')

