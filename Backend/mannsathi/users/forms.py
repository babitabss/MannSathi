from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from .models import User

class RegisterForm(UserCreationForm):
    # Extra fields we want on the registration form
    email         = forms.EmailField(required=True)
    phone         = forms.CharField(max_length=15, required=False)
    district      = forms.ChoiceField(choices=User.DISTRICT_CHOICES, required=False)
    language_pref = forms.ChoiceField(choices=User.LANGUAGE_CHOICES, required=False)

    class Meta:
        model  = User
        fields = [
            'username',
            'email',
            'phone',
            'district',
            'language_pref',
            'password1',
            'password2',
        ]
    
    
class ProfileUpdateForm(forms.ModelForm):

    class Meta:
        model  = User
        fields = [
            'first_name',
            'last_name',
            'email',
            'phone',
            'district',
            'language_pref',
            'bio',
            'avatar',
            'date_of_birth',
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'bio': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Tell us a little about yourself...'
            }),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Exclude current user when checking for duplicate email
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This email is already in use.")
        return email    