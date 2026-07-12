from django.contrib import admin
from .models import Post, Comment

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display  = ['title', 'user', 'category', 'is_anonymous', 'created_at']
    list_filter   = ['category', 'is_anonymous']
    search_fields = ['title', 'content', 'user__username']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display  = ['post', 'user', 'is_anonymous', 'created_at']
    search_fields = ['content', 'user__username']