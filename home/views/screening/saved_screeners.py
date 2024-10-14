from django.shortcuts import render


def default(request):
    return render(
        request=request,
        template_name='pages/screening/saved_screeners.html',
        context= {
            'parent': 'screening',
            'segment': 'saved_screeners',
        })