from django.shortcuts import render


def default(request):
    return render(
        request=request,
        template_name='pages/cash_flow/cash_overview.html',
        context= {
            'parent': 'cash_flow',
            'segment': 'cash_overview',
        })