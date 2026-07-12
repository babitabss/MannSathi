from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from .models import MoodEntry, CounselorProfile, Booking, Review, Payment
from .emails import (
    send_verification_approved_email,
    send_verification_rejected_email,
    send_booking_confirmation_email,
)
from notifications.utils import notify_counselor_approved, notify_counselor_rejected


@admin.register(MoodEntry)
class MoodEntryAdmin(admin.ModelAdmin):
    list_display  = ['user', 'mood_score', 'date']
    list_filter   = ['mood_score']
    search_fields = ['user__username']


@admin.register(CounselorProfile)
class CounselorProfileAdmin(admin.ModelAdmin):
    list_display  = [
        'user',
        'license_number',
        'experience_years',
        'verification_status',
        'is_verified',
        'created_at',
        'document_links',
    ]
    list_filter     = ['verification_status', 'is_verified', 'language']
    search_fields   = ['user__username', 'license_number']
    readonly_fields = ['verified_by', 'verified_at', 'document_links', 'created_at']
    actions         = ['verify_counselors', 'reject_counselors']

    fieldsets = (
        ('Basic Information', {
            'fields': (
                'user', 'bio', 'specializations',
                'language', 'price_per_session', 'experience_years'
            )
        }),
        ('Submitted Documents', {
            'fields': (
                'license_number',
                'license_document',
                'certificate_photo',
                'government_id',
                'document_links',
            )
        }),
        ('Verification', {
            'fields': (
                'verification_status',
                'is_verified',
                'is_available',
                'verification_notes',
                'verified_by',
                'verified_at',
            )
        }),
    )

    def document_links(self, obj):
        from django.utils.safestring import mark_safe
        links = []
        if obj.license_document:
            links.append(f'<a href="{obj.license_document.url}" target="_blank">License</a>')
            if obj.certificate_photo:
                links.append(f'<a href="{obj.certificate_photo.url}" target="_blank">Certificate</a>')
                if obj.government_id:
                    links.append(f'<a href="{obj.government_id.url}" target="_blank">Gov ID</a>')
                    return mark_safe(" | ".join(links)) if links else "No documents"
                document_links.short_description = "Documents"

    def verify_counselors(self, request, queryset):
        for profile in queryset:
            profile.is_verified         = True
            profile.is_available        = True
            profile.verification_status = 'approved'
            profile.verified_by         = request.user
            profile.verified_at         = timezone.now()
            profile.save()
            notify_counselor_approved(profile)
            profile.user.is_counselor = True
            profile.user.save()
            try:
                send_verification_approved_email(profile)
            except Exception as e:
                self.message_user(request, f"Could not email {profile.user.email}: {e}", level='warning')
        self.message_user(request, f"{queryset.count()} counselor(s) approved.")
    verify_counselors.short_description = "Approve selected counselors"

    def reject_counselors(self, request, queryset):
        for profile in queryset:
            profile.is_verified         = False
            profile.is_available        = False
            profile.verification_status = 'rejected'
            profile.save()
            notify_counselor_rejected(profile)
            profile.user.is_counselor = False
            profile.user.save()
            try:
                send_verification_rejected_email(profile, reason=profile.verification_notes or "")
            except Exception as e:
                self.message_user(request, f"Could not email {profile.user.email}: {e}", level='warning')
        self.message_user(request, f"{queryset.count()} application(s) rejected.")
    reject_counselors.short_description = "Reject selected applications"


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display  = ['user', 'counselor', 'session_type', 'scheduled_at', 'status']
    list_filter   = ['status', 'session_type']
    search_fields = ['user__username']
    actions       = ['confirm_bookings']

    def confirm_bookings(self, request, queryset):
        for booking in queryset:
            booking.status = 'confirmed'
            booking.save()
            try:
                send_booking_confirmation_email(booking)
            except Exception:
                pass
        self.message_user(request, f"{queryset.count()} booking(s) confirmed.")
    confirm_bookings.short_description = "Confirm selected bookings"


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['booking', 'rating', 'created_at']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display    = ['user', 'booking', 'amount', 'status', 'created_at']
    list_filter     = ['status']
    search_fields   = ['user__username']
    readonly_fields = ['transaction_uuid', 'created_at', 'updated_at']