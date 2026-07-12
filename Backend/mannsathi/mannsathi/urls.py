from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('users.urls')),
    path('', include('mental.urls')),
    path('', include('finance.urls')),
    path('', include('community.urls')),
    path('', include('chat.urls')),
    path('', include('notifications.urls')),
    path('', lambda request: redirect('login')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)