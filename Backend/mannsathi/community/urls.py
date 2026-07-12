from django.urls import path
from . import views

urlpatterns = [
    path('community/',              views.community_feed, name='community_feed'),
    path('community/post/new/',     views.create_post,    name='create_post'),
    path('community/post/<int:pk>/', views.post_detail,   name='post_detail'),
    path('community/post/<int:pk>/like/',   views.like_post,   name='like_post'),
    path('community/post/<int:pk>/delete/', views.delete_post, name='delete_post'),
]