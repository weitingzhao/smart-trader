from django.shortcuts import render


def default(request):
    return render(
        request=request,
        template_name='pages/wishlist/stop_limit_setup.html',
        context= {
            'parent': 'wishlist',
            'segment': 'stop_limit_setup',
        })