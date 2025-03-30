from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('create_payment/<int:course_id>/', views.create_payment, name='create_payment'),
    path('execute_payment/<int:course_id>/', views.execute_payment, name='execute_payment'),
]
