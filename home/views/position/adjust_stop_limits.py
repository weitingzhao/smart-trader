from django.shortcuts import render


def default(request):
    return render(
        request=request,
        template_name='pages/position/adjust_stop_limits.html',
        context= {
            'parent': 'position',
            'segment': 'adjust_stop_limits',
        })