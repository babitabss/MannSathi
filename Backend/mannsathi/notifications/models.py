from django.db import models
from django.conf import settings


class Notification(models.Model):

    TYPE_CHOICES = [
        ('booking',   'New Booking'),
        ('payment',   'Payment Received'),
        ('session',   'Session Update'),
        ('review',    'New Review'),
        ('approved',  'Account Approved'),
    ]

    user       = models.ForeignKey(
                     settings.AUTH_USER_MODEL,
                     on_delete=models.CASCADE,
                     related_name='notifications'
                 )
    title      = models.CharField(max_length=255)
    message    = models.TextField()
    type       = models.CharField(max_length=20, choices=TYPE_CHOICES, default='booking')
    link       = models.CharField(max_length=255, blank=True, null=True)
    is_read    = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} — {self.title}"