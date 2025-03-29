
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),  # Include allauth URLs
    path('', include('courses.urls')),
    path('payments/', include('payments.urls')),
    path('instructors', include('instructors.urls')),
    path('users/', include('users.urls')),
]
