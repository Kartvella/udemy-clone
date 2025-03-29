from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.home, name='home'),
    path('course/<slug:slug>/', views.course_detail, name='course_detail'),
    path('course/<slug:course_slug>/<slug:lesson_slug>/', views.course_lesson, name='course_lesson'),
]
