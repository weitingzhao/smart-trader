from django.shortcuts import render


def default(request):
    return render(
        request=request,
        template_name='pages/cash_flow/cash_flow_history.html',
        context= {
            'parent': 'cash_flow',
            'segment': 'cash_flow_history',
        })