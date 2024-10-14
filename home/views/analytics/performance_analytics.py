from django.shortcuts import render


def default(request):
    return render(
        request=request,
        template_name='pages/analytics/performance_analytics.html',
        context= {
            'parent': 'analytics',
            'segment': 'performance_analytics',
        })