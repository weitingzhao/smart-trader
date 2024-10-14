from django.shortcuts import render


def default(request):
    return render(
        request=request,
        template_name='pages/settings/account_settings.html',
        context= {
            'parent': 'settings',
            'segment': 'account_settings',
        })