from django.shortcuts import render


def default(request):
    return render(
        request=request,
        template_name='pages/performance/calendar_view.html',
        context= {
            'parent': 'performance',
            'segment': 'calendar_view',
        })