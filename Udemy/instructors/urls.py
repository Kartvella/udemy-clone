from django.urls import path
from . import views

app_name = 'instructors'

urlpatterns = [
    path('courses/create/', views.create_course, name='create_course'),
    path('courses/<slug:slug>/edit/', views.edit_course, name='edit_course'),
    path('courses/<slug:slug>/delete/', views.delete_course, name='delete_course'),
    path('courses/<slug:course_slug>/add_lesson/', views.add_lesson, name='add_lesson'),
    path('courses/<slug:course_slug>/<slug:lesson_slug>/edit/', views.edit_lesson, name='edit_lesson'),

]
