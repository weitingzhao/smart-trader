from django.shortcuts import render


def default(request):
    return render(
        request=request,
        template_name='pages/analytics/risk_analysis.html',
        context= {
            'parent': 'analytics',
            'segment': 'risk_analysis',
        })