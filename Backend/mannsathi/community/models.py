from django.db import models
from django.conf import settings

class Post(models.Model):

    CATEGORY_CHOICES = [
        ('general',   'General'),
        ('anxiety',   'Anxiety'),
        ('depression','Depression'),
        ('finance',   'Financial Stress'),
        ('work',      'Work & Career'),
        ('family',    'Family'),
        ('study',     'Studies'),
        ('other',     'Other'),
    ]

    user         = models.ForeignKey(
                       settings.AUTH_USER_MODEL,
                       on_delete=models.CASCADE,
                       related_name='posts'
                   )
    title        = models.CharField(max_length=200)
    content      = models.TextField()
    category     = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
    is_anonymous = models.BooleanField(default=True)
    likes        = models.ManyToManyField(
                       settings.AUTH_USER_MODEL,
                       related_name='liked_posts',
                       blank=True
                   )
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def total_likes(self):
        return self.likes.count()

    def display_name(self):
        if self.is_anonymous:
            return "Anonymous"
        return self.user.username


class Comment(models.Model):

    post         = models.ForeignKey(
                       Post,
                       on_delete=models.CASCADE,
                       related_name='comments'
                   )
    user         = models.ForeignKey(
                       settings.AUTH_USER_MODEL,
                       on_delete=models.CASCADE,
                       related_name='comments'
                   )
    content      = models.TextField()
    is_anonymous = models.BooleanField(default=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post.title}"

    def display_name(self):
        if self.is_anonymous:
            return "Anonymous"
        return self.user.username