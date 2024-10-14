from django.shortcuts import render


def default(request):
    return render(
        request=request,
        template_name='pages/wishlist/position_sizing.html',
        context= {
            'parent': 'wishlist',
            'segment': 'position_sizing',
        })