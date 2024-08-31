from home import views
from django.urls import path

#all below path with portfolio
urlpatterns = [
    path('', views.portfolio.portfolio_list, name='portfolio_list'),
    path('<int:pk>/', views.portfolio.portfolio_detail, name='portfolio_detail'),
    path('add/', views.portfolio.add_portfolio, name='add_portfolio'),
    path('<int:pk>/add_item/', views.portfolio.add_portfolio_item, name='add_portfolio_item'),
    path('item/<int:pk>/transactions/', views.portfolio.transaction_history, name='transaction_history'),
]