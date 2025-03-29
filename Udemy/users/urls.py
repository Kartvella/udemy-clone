from django.urls import path
from . import views


app_name = 'users'

urlpatterns = [
    path('my_profile/<int:pk>', views.my_profile, name='my_profile' ),
    path('logout', views.logout_view, name='logout'),
]