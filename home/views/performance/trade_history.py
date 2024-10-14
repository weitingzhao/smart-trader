from django.shortcuts import render


def default(request):
    return render(
        request=request,
        template_name='pages/performance/trade_history.html',
        context= {
            'parent': 'performance',
            'segment': 'trade_history',
        })