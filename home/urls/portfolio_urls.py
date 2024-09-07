from home import views
from django.urls import path

#all below path with [portfolio]
urlpatterns = [

    # Get
    path('', views.portfolio.get_portfolios, name='portfolios'),
    path('<int:pk>/', views.portfolio.portfolio_detail, name='portfolio_detail'),
    path('<int:portfolio_id>/item/<int:portfolio_item_id>/transactions/',
         views.portfolio.get_transaction_history, name='transactions'),

    # Add
    path('add/', views.portfolio.add_portfolio, name='add_portfolio'),
    path('<int:pk>/add_item/', views.portfolio.add_portfolio_item, name='add_portfolio_item'),
    path('add/transaction/', views.portfolio.add_transaction, name='add_transaction'),

    # Delete
    path('delete/<str:transaction_id>/', views.portfolio.delete_transaction, name='delete_transaction'),


]