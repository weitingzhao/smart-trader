from django.http import JsonResponse
from django.shortcuts import render, redirect
from home.base_home import BaseHome

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

def settings_fundamental_company_info_fetching(request):
    if request.method != 'GET':
      return JsonResponse({'success': False, 'error': 'Invalid request method'})
    try:

        company_view = instance.service.fetching().symbol().fetch_symbols_info()
        return JsonResponse({'success': True, 'data': "\r\n".join(company_view)})
    except Exception as e:
      return JsonResponse({'success': False, 'error': str(e)})
