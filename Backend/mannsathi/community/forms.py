from django import forms
from .models import Post, Comment

class PostForm(forms.ModelForm):

    class Meta:
        model  = Post
        fields = ['title', 'content', 'category', 'is_anonymous']
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'Give your post a title'
            }),
            'content': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': 'Share what is on your mind. This is a safe space.'
            }),
        }
        labels = {
            'is_anonymous': 'Post anonymously'
        }


class CommentForm(forms.ModelForm):

    class Meta:
        model  = Comment
        fields = ['content', 'is_anonymous']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Write a supportive response...'
            }),
        }
        labels = {
            'is_anonymous': 'Comment anonymously'
        }