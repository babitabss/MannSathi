from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.urls import reverse
from django.conf import settings
from .models import MoodEntry, CounselorProfile, Booking, Review, Payment
from .forms import MoodEntryForm, CounselorProfileForm, BookingForm, ReviewForm
from .esewa import get_esewa_payment_data, verify_esewa_payment
from .khalti import initiate_khalti_payment, verify_khalti_payment
import base64
import json
from notifications.utils import (
    notify_booking_created,
    notify_payment_completed,
    notify_session_completed,
    notify_session_cancelled,
    notify_review_received,
)


# ── Mood Journal ────────────────────────────────────────────

@login_required
def mood_journal(request):
    entries = MoodEntry.objects.filter(user=request.user)
    from django.utils import timezone
    today       = timezone.now().date()
    today_entry = entries.filter(date=today).first()
    return render(request, 'mental/mood_journal.html', {
        'entries':     entries[:10],
        'today_entry': today_entry,
    })


@login_required
def add_mood(request):
    from django.utils import timezone
    today = timezone.now().date()
    if MoodEntry.objects.filter(user=request.user, date=today).exists():
        messages.info(request, "You have already logged your mood today.")
        return redirect('mood_journal')

    if request.method == 'POST':
        form = MoodEntryForm(request.POST)
        if form.is_valid():
            entry          = form.save(commit=False)
            entry.user     = request.user
            entry.emotions = form.cleaned_data['emotions']
            entry.triggers = form.cleaned_data['triggers']
            entry.save()
            messages.success(request, "Mood logged successfully.")
            return redirect('mood_journal')
    else:
        form = MoodEntryForm()
    return render(request, 'mental/add_mood.html', {'form': form})


@login_required
def mood_detail(request, pk):
    entry = get_object_or_404(MoodEntry, pk=pk, user=request.user)
    return render(request, 'mental/mood_detail.html', {'entry': entry})


# ── Counselors ──────────────────────────────────────────────

@login_required
def counselor_list(request):
    specialization = request.GET.get('specialization', '')
    counselors     = CounselorProfile.objects.filter(is_verified=True, is_available=True)
    if specialization:
        counselors = [c for c in counselors if specialization in c.specializations]
    return render(request, 'mental/counselor_list.html', {
        'counselors':      counselors,
        'specialization':  specialization,
        'specializations': CounselorProfile.SPECIALIZATION_CHOICES,
    })


@login_required
def counselor_detail(request, pk):
    counselor = get_object_or_404(CounselorProfile, pk=pk, is_verified=True)
    reviews   = Review.objects.filter(booking__counselor=counselor)
    return render(request, 'mental/counselor_detail.html', {
        'counselor': counselor,
        'reviews':   reviews,
    })


@login_required
def book_session(request, pk):
    counselor = get_object_or_404(CounselorProfile, pk=pk, is_verified=True)
    if request.user == counselor.user:
        messages.error(request, "You cannot book your own session.")
        return redirect('counselor_list')

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking           = form.save(commit=False)
            booking.user      = request.user
            booking.counselor = counselor
            booking.save()
            notify_booking_created(booking)
            messages.success(request, "Session booked! Please complete payment to confirm.")
            return redirect('initiate_payment', booking_pk=booking.pk)
    else:
        form = BookingForm()
    return render(request, 'mental/book_session.html', {
        'form':      form,
        'counselor': counselor,
    })


@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user)
    return render(request, 'mental/my_bookings.html', {'bookings': bookings})


@login_required
def add_review(request, booking_pk):
    booking = get_object_or_404(Booking, pk=booking_pk, user=request.user, status='completed')
    if hasattr(booking, 'review'):
        messages.info(request, "You have already reviewed this session.")
        return redirect('my_bookings')

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review         = form.save(commit=False)
            review.booking = booking
            review.save()
            notify_review_received(review)
            messages.success(request, "Review submitted. Thank you.")
            return redirect('my_bookings')
    else:
        form = ReviewForm()
    return render(request, 'mental/add_review.html', {'form': form, 'booking': booking})


@login_required
def become_counselor(request):
    if hasattr(request.user, 'counselor_profile'):
        profile = request.user.counselor_profile
        if profile.verification_status == 'pending':
            messages.info(request, "Your application is under review.")
        elif profile.verification_status == 'rejected':
            messages.error(request, f"Your application was rejected: {profile.verification_notes or 'Contact support.'}")
        else:
            messages.info(request, "You are already a verified counselor.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = CounselorProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile                 = form.save(commit=False)
            profile.user            = request.user
            profile.specializations = form.cleaned_data['specializations']
            profile.save()
            messages.success(request, "Application submitted. We will review within 48 hours.")
            return redirect('dashboard')
    else:
        form = CounselorProfileForm()
    return render(request, 'mental/become_counselor.html', {'form': form})


# ── Counselor Dashboard ─────────────────────────────────────

@login_required
def counselor_bookings(request):
    if not hasattr(request.user, 'counselor_profile'):
        messages.error(request, "You are not registered as a counselor.")
        return redirect('dashboard')

    profile  = request.user.counselor_profile
    bookings = Booking.objects.filter(counselor=profile).select_related('user')
    return render(request, 'mental/counselor_bookings.html', {
        'profile':  profile,
        'bookings': bookings,
    })


@login_required
def counselor_profile_edit(request):
    if not hasattr(request.user, 'counselor_profile'):
        messages.error(request, "You are not registered as a counselor.")
        return redirect('dashboard')

    profile = request.user.counselor_profile

    if request.method == 'POST':
        form = CounselorProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            p                 = form.save(commit=False)
            p.specializations = form.cleaned_data['specializations']
            p.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('counselor_bookings')
    else:
        form = CounselorProfileForm(instance=profile)

    return render(request, 'mental/counselor_profile_edit.html', {
        'form':    form,
        'profile': profile,
    })


@login_required
def update_booking_status(request, pk):
    if not hasattr(request.user, 'counselor_profile'):
        messages.error(request, "You are not registered as a counselor.")
        return redirect('dashboard')

    booking = get_object_or_404(Booking, pk=pk, counselor=request.user.counselor_profile)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        allowed    = ['confirmed', 'completed', 'cancelled']
        if new_status in allowed:
            booking.status = new_status
            booking.save()
            if new_status == 'completed':
                notify_session_completed(booking)
            elif new_status == 'cancelled':
                notify_session_cancelled(booking)
            messages.success(request, f"Session marked as {new_status}.")
        else:
            messages.error(request, "Invalid status.")

    return redirect('counselor_bookings')


# ── Payment — Gateway Selection ─────────────────────────────

@login_required
def initiate_payment(request, booking_pk):
    booking = get_object_or_404(Booking, pk=booking_pk, user=request.user)

    if booking.status == 'cancelled':
        messages.error(request, "This booking has been cancelled.")
        return redirect('my_bookings')

    if hasattr(booking, 'payment') and booking.payment.status == 'completed':
        messages.info(request, "This booking is already paid.")
        return redirect('my_bookings')

    payment, _ = Payment.objects.get_or_create(
        booking=booking,
        defaults={
            'user':   request.user,
            'amount': booking.counselor.price_per_session,
        }
    )

    esewa_success_url = request.build_absolute_uri(reverse('esewa_success'))
    esewa_failure_url = request.build_absolute_uri(reverse('esewa_failure'))
    esewa_data        = get_esewa_payment_data(payment, esewa_success_url, esewa_failure_url)

    return render(request, 'mental/payment.html', {
        'booking':    booking,
        'payment':    payment,
        'esewa_data': esewa_data,
        'esewa_url':  settings.ESEWA_PAYMENT_URL,
    })


# ── eSewa Callbacks ─────────────────────────────────────────

@csrf_exempt
def esewa_success(request):
    encoded_data = request.GET.get('data', '')
    if not encoded_data:
        messages.error(request, "Invalid payment response from eSewa.")
        return redirect('my_bookings')

    try:
        decoded = json.loads(base64.b64decode(encoded_data).decode('utf-8'))
    except Exception:
        messages.error(request, "Could not read eSewa response. Please contact support.")
        return redirect('my_bookings')

    transaction_uuid = decoded.get('transaction_uuid')
    status           = decoded.get('status')

    # eSewa returns total_amount as "500.0" but we need "500" for the verify API
    raw_amount   = decoded.get('total_amount', '0')
    total_amount = str(int(float(raw_amount)))

    if status != 'COMPLETE':
        messages.error(request, f"eSewa returned status '{status}'. Payment not completed.")
        return redirect('my_bookings')

    try:
        payment = Payment.objects.get(transaction_uuid=transaction_uuid)
    except Payment.DoesNotExist:
        messages.error(request, "Payment record not found. Please contact support.")
        return redirect('my_bookings')

    # Already processed — don't double-confirm on page refresh
    if payment.status == 'completed':
        return render(request, 'mental/payment_success.html', {
            'payment': payment,
            'booking': payment.booking,
            'gateway': 'eSewa',
        })

    verified, verify_data = verify_esewa_payment(transaction_uuid, total_amount)

    if verified:
        payment.status       = 'completed'
        payment.gateway      = 'esewa'
        payment.esewa_ref_id = decoded.get('transaction_code', '')
        payment.save()
        payment.booking.status = 'confirmed'
        payment.booking.save()
        
        if not payment.booking.jitsi_room:
            payment.booking.jitsi_room = f"mannsaathi-booking-{payment.booking.pk}"
            payment.booking.save()
            notify_payment_completed(payment)

        # Notify counselor by email
        try:
            from django.core.mail import send_mail
            counselor_email = payment.booking.counselor.user.email
            client_name     = payment.user.get_full_name() or payment.user.username
            session_date    = payment.booking.scheduled_at.strftime('%B %d, %Y at %I:%M %p')
            send_mail(
                subject='New Booking Confirmed — MannSaathi',
                message=f'''Hello,

A new client has booked and paid for a session with you.

Client:       {client_name}
Session Type: {payment.booking.get_session_type_display()}
Date & Time:  {session_date}
Amount Paid:  NPR {payment.amount} via eSewa

Log in to your counselor dashboard to view the session:
http://127.0.0.1:8000/counselor/sessions/

— MannSaathi Team''',
                from_email='noreply@mannsaathi.com',
                recipient_list=[counselor_email],
                fail_silently=True,
            )
        except Exception:
            pass

        return render(request, 'mental/payment_success.html', {
            'payment': payment,
            'booking': payment.booking,
            'gateway': 'eSewa',
        })
    else:
        return render(request, 'mental/payment_failure.html', {
            'gateway': 'eSewa',
            'booking': payment.booking,
        })


def esewa_failure(request):
    transaction_uuid = request.GET.get('transaction_uuid', '')
    booking = None
    try:
        if transaction_uuid:
            payment = Payment.objects.get(transaction_uuid=transaction_uuid)
            booking = payment.booking
    except Payment.DoesNotExist:
        pass
    return render(request, 'mental/payment_failure.html', {
        'gateway': 'eSewa',
        'booking': booking,
    })


# ── Khalti Callbacks ────────────────────────────────────────

@login_required
def khalti_initiate(request, booking_pk):
    booking = get_object_or_404(Booking, pk=booking_pk, user=request.user)

    if hasattr(booking, 'payment') and booking.payment.status == 'completed':
        messages.info(request, "This booking is already paid.")
        return redirect('my_bookings')

    payment, _ = Payment.objects.get_or_create(
        booking=booking,
        defaults={
            'user':   request.user,
            'amount': booking.counselor.price_per_session,
        }
    )
    payment.gateway = 'khalti'
    payment.save()

    return_url = request.build_absolute_uri(reverse('khalti_verify'))

    try:
        pidx, payment_url = initiate_khalti_payment(payment, return_url=return_url)
        payment.khalti_pidx = pidx
        payment.save()
        return redirect(payment_url)
    except Exception as e:
        messages.error(request, f"Could not connect to Khalti: {e}")
        return redirect('initiate_payment', booking_pk=booking_pk)


def khalti_verify(request):
    pidx   = request.GET.get('pidx', '')
    status = request.GET.get('status', '')

    if status != 'Completed' or not pidx:
        booking = None
        try:
            if pidx:
                payment = Payment.objects.get(khalti_pidx=pidx)
                booking = payment.booking
        except Payment.DoesNotExist:
            pass
        return render(request, 'mental/payment_failure.html', {
            'gateway': 'Khalti',
            'booking': booking,
        })

    try:
        payment = Payment.objects.get(khalti_pidx=pidx)
    except Payment.DoesNotExist:
        messages.error(request, "Payment record not found. Please contact support.")
        return redirect('my_bookings')

    # Already processed — don't double-confirm on page refresh
    if payment.status == 'completed':
        return render(request, 'mental/payment_success.html', {
            'payment': payment,
            'booking': payment.booking,
            'gateway': 'Khalti',
        })

    verified, data = verify_khalti_payment(pidx)

    if verified:
        payment.status        = 'completed'
        payment.khalti_txn_id = data.get('transaction_id', '')
        payment.save()
        payment.booking.status = 'confirmed'
        payment.booking.save()
        notify_payment_completed(payment)
        
        if not payment.booking.jitsi_room:
            payment.booking.jitsi_room = f"mannsaathi-booking-{payment.booking.pk}"
            payment.booking.save()

        # Notify counselor by email
        try:
            from django.core.mail import send_mail
            counselor_email = payment.booking.counselor.user.email
            client_name     = payment.user.get_full_name() or payment.user.username
            session_date    = payment.booking.scheduled_at.strftime('%B %d, %Y at %I:%M %p')
            send_mail(
                subject='New Booking Confirmed — MannSaathi',
                message=f'''Hello,

A new client has booked and paid for a session with you.

Client:       {client_name}
Session Type: {payment.booking.get_session_type_display()}
Date & Time:  {session_date}
Amount Paid:  NPR {payment.amount} via Khalti
Session Room: https://meet.jit.si/mannsaathi-booking-{payment.booking.pk}

Log in to your counselor dashboard to view the session:
http://127.0.0.1:8000/counselor/sessions/

— MannSaathi Team''',
                from_email='noreply@mannsaathi.com',
                recipient_list=[counselor_email],
                fail_silently=True,
            )
        except Exception:
            pass

        return render(request, 'mental/payment_success.html', {
            'payment': payment,
            'booking': payment.booking,
            'gateway': 'Khalti',
        })
    else:
        return render(request, 'mental/payment_failure.html', {
            'gateway': 'Khalti',
            'booking': payment.booking,
        })