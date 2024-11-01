from django.urls import path
from home.views import position

#all below path with [position]
urlpatterns = [

    path('add/', position.transaction.add, name='add_transaction'),

    path('<int:transaction_id>/', position.transaction.get, name='get_transaction'),

    path('<int:transaction_id>/update/', position.transaction.update,  name='update_transaction'),

    path('<int:transaction_id>/delete/', position.transaction.delete,  name='delete_transaction'),

]