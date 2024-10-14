from django.shortcuts import render


def default(request):
    return render(
        request=request,
        template_name='pages/settings/risk_preferences.html',
        context= {
            'parent': 'settings',
            'segment': 'risk_preferences',
        })