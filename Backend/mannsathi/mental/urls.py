from django.urls import path
from . import views

urlpatterns = [
    # Mood Journal
    path('mood/',                              views.mood_journal,  name='mood_journal'),
    path('mood/add/',                          views.add_mood,      name='add_mood'),
    path('mood/<int:pk>/',                     views.mood_detail,   name='mood_detail'),

    # Counselors
    path('counselors/',                        views.counselor_list,    name='counselor_list'),
    path('counselors/<int:pk>/',               views.counselor_detail,  name='counselor_detail'),
    path('counselors/<int:pk>/book/',          views.book_session,      name='book_session'),
    path('counselors/become/',                 views.become_counselor,  name='become_counselor'),

    # User bookings
    path('bookings/',                          views.my_bookings,  name='my_bookings'),
    path('bookings/<int:booking_pk>/review/',  views.add_review,   name='add_review'),

    # Payment
    path('payment/<int:booking_pk>/',          views.initiate_payment, name='initiate_payment'),

    # eSewa
    path('payment/esewa/success/',             views.esewa_success, name='esewa_success'),
    path('payment/esewa/failure/',             views.esewa_failure, name='esewa_failure'),

    # Khalti
    path('payment/khalti/<int:booking_pk>/',   views.khalti_initiate, name='khalti_initiate'),
    path('payment/khalti/verify/',             views.khalti_verify,   name='khalti_verify'),

    # Counselor dashboard
    path('counselor/sessions/',                views.counselor_bookings,     name='counselor_bookings'),
    path('counselor/profile/edit/',            views.counselor_profile_edit, name='counselor_profile_edit'),
    path('counselor/session/<int:pk>/update/', views.update_booking_status,  name='update_booking_status'),
]