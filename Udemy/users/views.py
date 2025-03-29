from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import logout


def my_profile(request, pk):
    pass


def logout_view(request):
    logout(request)
    return redirect('courses:home')