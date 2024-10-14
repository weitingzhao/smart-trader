from django.shortcuts import render


def default(request):
    return render(
        request=request,
        template_name='pages/wishlist/wishlist_overview.html',
        context= {
            'parent': 'wishlist',
            'segment': 'wishlist_overview',
        })