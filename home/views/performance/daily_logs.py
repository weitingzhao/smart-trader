from django.shortcuts import render


def default(request):
    return render(
        request=request,
        template_name='pages/performance/daily_logs.html',
        context= {
            'parent': 'performance',
            'segment': 'daily_logs',
        })