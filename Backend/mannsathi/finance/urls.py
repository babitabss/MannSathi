from django.urls import path
from . import views

urlpatterns = [
    path('finance/',                      views.finance_dashboard, name='finance_dashboard'),
    path('finance/add/',                  views.add_transaction,   name='add_transaction'),
    path('finance/delete/<int:pk>/',      views.delete_transaction, name='delete_transaction'),
    path('finance/goal/add/',             views.add_goal,          name='add_goal'),
    path('finance/goal/delete/<int:pk>/', views.delete_goal,       name='delete_goal'),
]