from django import forms
from .models import MoodEntry, CounselorProfile, Booking, Review

class MoodEntryForm(forms.ModelForm):

    # Render emotions as checkboxes
    emotions = forms.MultipleChoiceField(
        choices=MoodEntry.EMOTION_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    # Render triggers as checkboxes
    triggers = forms.MultipleChoiceField(
        choices=MoodEntry.TRIGGER_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model  = MoodEntry
        fields = ['mood_score', 'emotions', 'triggers', 'notes']
        widgets = {
            'mood_score': forms.RadioSelect,
            'notes': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Write anything on your mind today... (only you can see this)'
            }),
        }
        

class CounselorProfileForm(forms.ModelForm):

    specializations = forms.MultipleChoiceField(
        choices=CounselorProfile.SPECIALIZATION_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    class Meta:
        model  = CounselorProfile
        fields = [
            'bio',
            'specializations',
            'language',
            'price_per_session',
            'experience_years',
            'license_number',
            'license_document',
            'certificate_photo',
            'government_id',
        ]
        widgets = {
            'bio': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Describe your background, approach and experience...'
            }),
            'license_number': forms.TextInput(attrs={
                'placeholder': 'e.g. NHPC-2024-12345'
            }),
        }
        labels = {
            'license_document':  'License Document (PDF or image)',
            'certificate_photo': 'Degree / Training Certificate',
            'government_id':     'Government ID (Citizenship or Passport)',
        }

    def clean_price_per_session(self):
        price = self.cleaned_data.get('price_per_session')
        if price and price < 100:
            raise forms.ValidationError(
                "Minimum session price is NPR 100."
            )
        return price

    def clean_license_document(self):
        doc = self.cleaned_data.get('license_document')
        if doc:
            # Max 5MB
            if doc.size > 5 * 1024 * 1024:
                raise forms.ValidationError(
                    "File size must be under 5MB."
                )
            # Only allow PDF and images
            allowed = ['.pdf', '.jpg', '.jpeg', '.png']
            import os
            ext = os.path.splitext(doc.name)[1].lower()
            if ext not in allowed:
                raise forms.ValidationError(
                    "Only PDF, JPG and PNG files are allowed."
                )
        return doc


class BookingForm(forms.ModelForm):

    class Meta:
        model  = Booking
        fields = ['session_type', 'scheduled_at', 'note']
        widgets = {
            'scheduled_at': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
            'note': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Briefly describe what you would like to discuss (optional)'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['scheduled_at'].input_formats = ['%Y-%m-%dT%H:%M']


class ReviewForm(forms.ModelForm):

    class Meta:
        model  = Review
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Share your experience with this counselor...'
            }),
        }        
        
        