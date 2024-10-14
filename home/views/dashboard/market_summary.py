from django.shortcuts import render


def default(request):
    return render(
        request=request,
        template_name='pages/dashboard/market_summary.html',
        context= {
            'parent': 'dashboard',
            'segment': 'market_summary',
        })