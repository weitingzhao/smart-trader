from django.shortcuts import render


def default(request):
    return render(
        request=request,
        template_name='pages/screening/screening_results.html',
        context= {
            'parent': 'screening',
            'segment': 'screening_results',
        })