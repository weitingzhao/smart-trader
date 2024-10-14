from django.shortcuts import render


def default(request):
    return render(
        request=request,
        template_name='pages/dashboard/overview.html',
        context= {
            'parent': 'dashboard',
            'segment': 'overview',
        })