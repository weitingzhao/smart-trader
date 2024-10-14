from django.shortcuts import render


def default(request):
    return render(
        request=request,
        template_name='pages/position/close_positions.html',
        context= {
            'parent': 'position',
            'segment': 'close_positions',
        })