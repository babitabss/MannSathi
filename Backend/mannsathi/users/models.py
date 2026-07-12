from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('ne', 'Nepali')
    ]
    
    DISTRICT_CHOICES = [
        ('kathmandu', 'Kathmandu'),
        ('pokhara', 'Pokhara'),
        ('lalitpur', 'Lalitpur'),
        ('bhaktapur', 'Bhaktapur'),
        ('chitwan', 'Chitwan'),
        ('butwal', 'Butwal'),
        ('other', 'Other'),
    ]
    groups = models.ManyToManyField('auth.Group', related_name='mannsathi_users', blank=True)
    user_permissions = models.ManyToManyField('auth.Permission', related_name='mannsathi_users', blank=True)
    
    phone =models.CharField(max_length=15, blank=True, null=True)
    district =models.CharField(max_length=50, choices=DISTRICT_CHOICES, blank= True, null= True)
    language_pref=models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default= 'en')
    is_counselor =models.BooleanField(default=False)
    bio =models.TextField(blank=True, null=True)
    avatar =models.ImageField(upload_to='avatars/', blank=True, null=True)
    date_of_birth =models.DateField(blank=True, null=True)
    created_at =models.DateTimeField(auto_now_add=True)
    updated_at =models.DateTimeField(auto_now= True)
    
    def __str__(self):
        return self.username
    
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username
    