from django.urls import reverse
from home.base_home import BaseHome
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from home.models import MarketStockHistoricalBars

# Create your views here.
instance = BaseHome()

# Pages
def index(request):
    return render(request, 'pages/index.html', {'segment': 'index'})


def billing(request):
    return render(request, 'pages/billing.html', {'segment': 'billing'})
def tables(request):
    return render(request, 'pages/tables.html', {'segment': 'tables'})
def profile(request):
    return render(request, 'pages/profile.html', {'segment': 'profile'})




# from .models import Question
# def detail(request, question_id):
#     latest_question_list = Question.objects.order_by("-pub_date")[:5]
#     output = ", ".join([q.question_text for q in latest_question_list])
#     return HttpResponse(output)
# def results(request, question_id):
#     response = "You're looking at the results of question %s."
#     return HttpResponse(response % question_id)
# def vote(request, question_id):
#     return HttpResponse("You're voting on question %s." % question_id)

