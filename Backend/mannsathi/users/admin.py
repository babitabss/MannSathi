from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display   = ['username', 'email', 'role', 'district', 'language_pref', 'created_at']
    search_fields  = ['username', 'email', 'phone']
    list_filter    = ['is_counselor', 'district', 'language_pref']

    fieldsets = UserAdmin.fieldsets + (
        ('MannSaathi Info', {
            'fields': ('phone', 'district', 'language_pref', 'is_counselor', 'bio', 'avatar', 'date_of_birth')
        }),
    )

    def role(self, obj):
        # Check if they have a counselor profile (pending or approved)
        if obj.is_counselor:
            return ' Counselor (Verified)'
        elif hasattr(obj, 'counselor_profile'):
            return ' Counselor (Pending)'
        else:
            return ' Client'
    role.short_description = 'Role'