from django.db import models
from django.conf import settings
import uuid

class MoodEntry(models.Model):

    # Mood score choices — 1 to 5
    MOOD_CHOICES = [
        (1, 'Very Bad'),
        (2, 'Bad'),
        (3, 'Neutral'),
        (4, 'Good'),
        (5, 'Very Good'),
    ]

    # Emotion tags user can select
    EMOTION_CHOICES = [
        ('anxious',    'Anxious'),
        ('lonely',     'Lonely'),
        ('happy',      'Happy'),
        ('angry',      'Angry'),
        ('hopeful',    'Hopeful'),
        ('exhausted',  'Exhausted'),
        ('calm',       'Calm'),
        ('sad',        'Sad'),
        ('grateful',   'Grateful'),
        ('stressed',   'Stressed'),
    ]

    # Trigger choices — what caused this mood
    TRIGGER_CHOICES = [
        ('exams',         'Exams'),
        ('family',        'Family'),
        ('work',          'Work'),
        ('money',         'Money'),
        ('relationships', 'Relationships'),
        ('health',        'Health'),
        ('social',        'Social Media'),
        ('other',         'Other'),
    ]

    user       = models.ForeignKey(
                     settings.AUTH_USER_MODEL,
                     on_delete=models.CASCADE,
                     related_name='mood_entries'
                 )
    mood_score = models.IntegerField(choices=MOOD_CHOICES)
    emotions   = models.JSONField(default=list, blank=True)
    triggers   = models.JSONField(default=list, blank=True)
    notes      = models.TextField(blank=True, null=True)
    date       = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        # One entry per user per day
        unique_together = ['user', 'date']

    def __str__(self):
        return f"{self.user.username} — {self.get_mood_score_display()} on {self.date}"

    def mood_label(self):
        return self.get_mood_score_display()
    
    
class CounselorProfile(models.Model):

    SPECIALIZATION_CHOICES = [
        ('anxiety',    'Anxiety'),
        ('depression', 'Depression'),
        ('stress',     'Stress Management'),
        ('grief',      'Grief & Loss'),
        ('trauma',     'Trauma'),
        ('finance',    'Financial Stress'),
        ('career',     'Career & Study'),
        ('family',     'Family Issues'),
        ('general',    'General Counseling'),
    ]

    LANGUAGE_CHOICES = [
        ('nepali',  'Nepali'),
        ('english', 'English'),
        ('both',    'Both'),
    ]
    
    VERIFICATION_STATUS = [
        ('pending',  'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user             = models.OneToOneField(
                           settings.AUTH_USER_MODEL,
                           on_delete=models.CASCADE,
                           related_name='counselor_profile'
                       )
    bio              = models.TextField()
    specializations  = models.JSONField(default=list)
    language         = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default='both')
    price_per_session = models.DecimalField(max_digits=8, decimal_places=2)
    experience_years = models.IntegerField(default=0)
    is_verified      = models.BooleanField(default=False)
    is_available     = models.BooleanField(default=True)
    license_number   = models.CharField(max_length=100, blank=True, null=True)
    license_document    = models.FileField(upload_to='counselor_docs/',blank=True, null=True)
    certificate_photo   = models.FileField(upload_to='counselor_docs/',blank=True, null=True)
    government_id       = models.FileField(upload_to='counselor_docs/',blank=True, null=True)
    verification_notes  = models.TextField(blank=True, null=True)
    verification_status = models.CharField(max_length=10,choices=VERIFICATION_STATUS,default='pending')
    verified_by         = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True, blank=True,related_name='verified_counselors')
    verified_at         = models.DateTimeField(null=True, blank=True)
    created_at       = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} — {self.get_verification_status_display()}"

    def average_rating(self):
        reviews = Review.objects.filter(booking__counselor=self)
        if not reviews.exists():
            return 0
        total = sum(r.rating for r in reviews)
        return round(total / reviews.count(), 1)


class Booking(models.Model):

    SESSION_CHOICES = [
        ('video', 'Video Call'),
        ('voice', 'Voice Call'),
        ('text',  'Text Chat'),
    ]

    STATUS_CHOICES = [
        ('pending',   'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    user         = models.ForeignKey(
                       settings.AUTH_USER_MODEL,
                       on_delete=models.CASCADE,
                       related_name='bookings'
                   )
    counselor    = models.ForeignKey(
                       CounselorProfile,
                       on_delete=models.CASCADE,
                       related_name='bookings'
                   )
    session_type  = models.CharField(max_length=10, choices=SESSION_CHOICES)
    scheduled_at  = models.DateTimeField()
    status        = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    note          = models.TextField(blank=True, null=True)
    created_at    = models.DateTimeField(auto_now_add=True)
    jitsi_room    = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ['-scheduled_at']

    def __str__(self):
        return f"{self.user.username} with {self.counselor} on {self.scheduled_at}"
    
    def get_jitsi_url(self):
        return f"https://meet.jit.si/mannsaathi-booking-{self.pk}"


class Review(models.Model):

    booking   = models.OneToOneField(
                    Booking,
                    on_delete=models.CASCADE,
                    related_name='review'
                )
    rating    = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment   = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.booking}"    
    
class Payment(models.Model):

    GATEWAY_CHOICES = [
        ('esewa',  'eSewa'),
        ('khalti', 'Khalti'),
    ]

    STATUS_CHOICES = [
        ('pending',   'Pending'),
        ('completed', 'Completed'),
        ('failed',    'Failed'),
        ('refunded',  'Refunded'),
    ]

    user             = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payment')
    booking          = models.OneToOneField('Booking', on_delete=models.CASCADE, related_name='payment')
    transaction_uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    amount           = models.DecimalField(max_digits=10, decimal_places=2)
    gateway          = models.CharField(max_length=10, choices=GATEWAY_CHOICES, default='esewa')
    status           = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    esewa_ref_id     = models.CharField(max_length=255, blank=True, null=True)
    khalti_pidx      = models.CharField(max_length=255, blank=True, null=True)
    khalti_txn_id    = models.CharField(max_length=255, blank=True, null=True)
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment {self.transaction_uuid} via {self.gateway} — {self.status}"