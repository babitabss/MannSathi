from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from mental.models import Booking
from .models import ChatMessage


@login_required
def chat_room(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)

    # Only client or counselor of this booking can access
    if request.user != booking.user and request.user != booking.counselor.user:
        messages.error(request, "You are not allowed to access this chat.")
        return redirect('dashboard')

    if booking.status not in ['confirmed', 'completed']:
        messages.error(request, "Chat is only available for confirmed sessions.")
        return redirect('my_bookings')

    chat_messages = ChatMessage.objects.filter(booking=booking).select_related('sender')

    return render(request, 'chat/chat_room.html', {
        'booking':       booking,
        'chat_messages': chat_messages,
        'other_user':    booking.counselor.user if request.user == booking.user else booking.user,
    })