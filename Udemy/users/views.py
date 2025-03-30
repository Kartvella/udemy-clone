from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from courses.models import Course
from django.contrib.auth.models import User
 
@login_required
def my_profile(request, pk):
    user = get_object_or_404(User.objects.prefetch_related('enrollments__course', 'courses'), pk=pk)

    if request.user == user:
        enrolled_courses = Course.objects.filter(enrollments__user=user).select_related('instructor', 'topic')

        created_courses = Course.objects.filter(instructor=user).select_related('topic')

        context = {
            "user_profile": user,
            "enrolled_courses": enrolled_courses,
            "created_courses": created_courses,
        }

        return render(request, "users/my_profile.html", context)
    else:
        return HttpResponse('You are not supposed to be here!')

@login_required
def logout_view(request):
    logout(request)
    return redirect('courses:home')