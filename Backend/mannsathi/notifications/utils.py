from .models import Notification


def notify(user, title, message, type='booking', link=None):
    """
    Create a notification for a user.
    Call this from anywhere in the project.
    """
    Notification.objects.create(
        user=user,
        title=title,
        message=message,
        type=type,
        link=link,
    )


def notify_booking_created(booking):
    """Counselor gets notified when client books"""
    notify(
        user=booking.counselor.user,
        title='New Session Booking',
        message=f'{booking.user.get_full_name() or booking.user.username} has booked a {booking.get_session_type_display()} session with you on {booking.scheduled_at.strftime("%B %d, Y at %I:%M %p")}.',
        type='booking',
        link='/counselor/sessions/',
    )


def notify_payment_completed(payment):
    """Client + Counselor get notified after payment"""
    booking      = payment.booking
    client_name  = booking.user.get_full_name() or booking.user.username
    counselor_name = booking.counselor.user.get_full_name() or booking.counselor.user.username
    session_date = booking.scheduled_at.strftime('%B %d, %Y at %I:%M %p')

    # Notify client
    notify(
        user=booking.user,
        title='Booking Confirmed',
        message=f'Your session with {counselor_name} on {session_date} is confirmed. NPR {payment.amount} paid via {payment.get_gateway_display()}.',
        type='payment',
        link='/bookings/',
    )

    # Notify counselor
    notify(
        user=booking.counselor.user,
        title='Payment Received',
        message=f'{client_name} has paid NPR {payment.amount} for their {booking.get_session_type_display()} session on {session_date}.',
        type='payment',
        link='/counselor/sessions/',
    )


def notify_session_completed(booking):
    """Client gets notified when counselor marks session done"""
    counselor_name = booking.counselor.user.get_full_name() or booking.counselor.user.username
    notify(
        user=booking.user,
        title='Session Completed',
        message=f'Your session with {counselor_name} has been marked as completed. Please leave a review!',
        type='session',
        link='/bookings/',
    )


def notify_session_cancelled(booking):
    """Client gets notified when counselor cancels"""
    counselor_name = booking.counselor.user.get_full_name() or booking.counselor.user.username
    notify(
        user=booking.user,
        title='Session Cancelled',
        message=f'Your session with {counselor_name} on {booking.scheduled_at.strftime("%B %d, %Y")} has been cancelled. Please contact support.',
        type='session',
        link='/bookings/',
    )


def notify_review_received(review):
    """Counselor gets notified when client leaves review"""
    client_name = review.booking.user.get_full_name() or review.booking.user.username
    notify(
        user=review.booking.counselor.user,
        title='New Review',
        message=f'{client_name} left you a {review.rating}-star review.',
        type='review',
        link='/counselor/sessions/',
    )


def notify_counselor_approved(profile):
    """Counselor gets notified when admin approves"""
    notify(
        user=profile.user,
        title='Application Approved!',
        message='Congratulations! Your counselor application has been approved. Your profile is now live and clients can book sessions with you.',
        type='approved',
        link='/counselor/sessions/',
    )


def notify_counselor_rejected(profile):
    """Counselor gets notified when admin rejects"""
    notify(
        user=profile.user,
        title='Application Update',
        message=f'Your counselor application was not approved. Reason: {profile.verification_notes or "Please contact support for more information."}',
        type='session',
        link='/counselors/become/',
    )


def notify_new_comment(comment):
    """Post author gets notified when someone comments"""
    if comment.user == comment.post.user:
        return  # Don't notify yourself
    commenter_name = comment.user.get_full_name() or comment.user.username
    notify(
        user=comment.post.user,
        title='New Comment',
        message=f'{commenter_name} commented on your post "{comment.post.title}".',
        type='review',
        link=f'/community/{comment.post.pk}/',
    )