from django.shortcuts import render


def default(request):
    return render(
        request=request,
        template_name='pages/performance/portfolio_performance.html',
        context= {
            'parent': 'performance',
            'segment': 'portfolio_performance',
        })