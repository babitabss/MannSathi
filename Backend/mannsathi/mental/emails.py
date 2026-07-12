from django.core.mail import send_mail
from django.conf import settings

def send_verification_approved_email(counselor_profile):
    user    = counselor_profile.user
    subject = "Your MannSaathi Counselor Application is Approved"
    message = f"""
Dear {user.get_full_name() or user.username},

Congratulations! Your counselor application on MannSaathi has been approved.

Your profile is now live and users can start booking sessions with you.

License Number: {counselor_profile.license_number}
Session Price:  NPR {counselor_profile.price_per_session}

You can manage your sessions by logging in at:
http://127.0.0.1:8000/login/

If you have any questions, reply to this email.

Warm regards,
MannSaathi Team
    """.strip()

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )


def send_verification_rejected_email(counselor_profile, reason=""):
    user    = counselor_profile.user
    subject = "Update on Your MannSaathi Counselor Application"
    message = f"""
Dear {user.get_full_name() or user.username},

Thank you for applying to be a counselor on MannSaathi.

After reviewing your application, we are unable to approve it at this time.

{"Reason: " + reason if reason else ""}

You are welcome to reapply after addressing the above issues.

If you believe this is a mistake, please contact us at support@mannsaathi.com.

Warm regards,
MannSaathi Team
    """.strip()

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )


def send_booking_confirmation_email(booking):
    user      = booking.user
    counselor = booking.counselor.user
    subject   = "Session Booking Confirmed — MannSaathi"
    message   = f"""
Dear {user.get_full_name() or user.username},

Your session has been confirmed.

Counselor:    {counselor.get_full_name() or counselor.username}
Session Type: {booking.get_session_type_display()}
Date & Time:  {booking.scheduled_at.strftime("%B %d, %Y at %I:%M %p")}

Please be ready 5 minutes before your session.

Warm regards,
MannSaathi Team
    """.strip()

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )