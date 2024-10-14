from django.shortcuts import render


def default(request):
    return render(
        request=request,
        template_name='pages/settings/notifications.html',
        context= {
            'parent': 'settings',
            'segment': 'notifications',
        })