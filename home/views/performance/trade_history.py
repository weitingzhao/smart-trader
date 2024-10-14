from django.shortcuts import render


def default(request):
    return render(
        request=request,
        template_name='pages/performance/trade_history.html',
        context= {
            'parent': 'screening',
            'segment': 'trade_history',
        })