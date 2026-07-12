from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from .forms import RegisterForm, ProfileUpdateForm
from mental.models import MoodEntry, Booking
from finance.models import Transaction, SavingsGoal
from community.models import Post

def register_view(request):
    # If user is already logged in, send them to dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        # Form was submitted — fill it with the submitted data
        form = RegisterForm(request.POST)

        if form.is_valid():
            # Save the new user to the database
            user = form.save()
            # Log them in immediately after registering
            login(request, user)
            messages.success(request, f"Welcome to MannSaathi, {user.username}!")
            return redirect('dashboard')
        # If form is invalid, fall through and show errors below

    else:
        # GET request — show empty form
        form = RegisterForm()

    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')


def dashboard_view(request):
    # Only logged in users can see this
    if not request.user.is_authenticated:
        return redirect('login')
    
    return render(request, 'users/dashboard.html', {'user': request.user})



@login_required
def profile_view(request):
    # Activity summary
    mood_count    = MoodEntry.objects.filter(user=request.user).count()
    booking_count = Booking.objects.filter(user=request.user).count()
    post_count    = Post.objects.filter(user=request.user).count()
    expense_total = Transaction.objects.filter(
                        user=request.user,
                        type='expense'
                    ).aggregate(
                        total=models.Sum('amount')
                    )['total'] or 0

    # Recent mood entries
    recent_moods = MoodEntry.objects.filter(user=request.user)[:5]

    return render(request, 'users/profile.html', {
        'user':          request.user,
        'mood_count':    mood_count,
        'booking_count': booking_count,
        'post_count':    post_count,
        'expense_total': expense_total,
        'recent_moods':  recent_moods,
    })


@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(
            request.POST,
            request.FILES,
            instance=request.user
        )
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(request, 'users/profile_edit.html', {'form': form})


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            # Keep user logged in after password change
            update_session_auth_hash(request, user)
            messages.success(request, "Password changed successfully.")
            return redirect('profile')
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, 'users/change_password.html', {'form': form})