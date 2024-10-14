from django.shortcuts import render


def default(request):
    return render(
        request=request,
        template_name='pages/dashboard/recent_activity.html',
        context= {
            'parent': 'dashboard',
            'segment': 'recent_activity',
        })