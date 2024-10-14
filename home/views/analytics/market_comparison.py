from django.shortcuts import render


def default(request):
    return render(
        request=request,
        template_name='pages/analytics/market_comparison.html',
        context= {
            'parent': 'analytics',
            'segment': 'market_comparison',
        })