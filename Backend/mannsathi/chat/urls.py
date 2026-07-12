from django.urls import path
from . import views

urlpatterns = [
    path('chat/<int:booking_id>/', views.chat_room, name='chat_room'),
]