from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from courses.models import Course, Lesson
from .forms import CourseCreateForm, LessonForm


@login_required
def create_course(request):
    if request.method == "POST":
        form = CourseCreateForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Course created successfully!")
            return redirect("courses:home")
    else:
        form = CourseCreateForm(user=request.user)

    return render(request, "instructors/create_course.html", {"form": form})

def add_lesson(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)

    if request.user != course.instructor:
        messages.error(request, "You do not have permission to add lessons to this course.")
        return redirect('courses:course_detail', slug=course.slug)

    if request.method == 'POST':
        form = LessonForm(request.POST, request.FILES)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.course = course
            lesson.save()
            messages.success(request, f"Lesson '{lesson.title}' added successfully.")
            return redirect('courses:course_detail', slug=course.slug)
    else:
        form = LessonForm()

    return render(request, 'instructors/add_lesson.html', {'form': form, 'course': course})

@login_required
def edit_course(request, slug):
    course = get_object_or_404(Course, slug=slug, instructor=request.user)

    if request.method == "POST":
        form = CourseCreateForm(request.POST, request.FILES, instance=course, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Course updated successfully!")
            return redirect("courses:home")
    else:
        form = CourseCreateForm(instance=course, user=request.user)

    return render(request, "instructors/edit_course.html", {"form": form, "course": course})

def edit_lesson(request, course_slug, lesson_slug):
    course = get_object_or_404(Course, slug=course_slug)
    lesson = get_object_or_404(Lesson, slug=lesson_slug, course=course)

    if request.user != course.instructor:
        messages.error(request, "You do not have permission to edit this lesson.")
        return redirect('courses:course_detail', slug=course.slug)

    if request.method == 'POST':
        form = LessonForm(request.POST, request.FILES, instance=lesson)
        if form.is_valid():
            form.save()
            messages.success(request, f"Lesson '{lesson.title}' updated successfully.")
            return redirect('courses:course_detail', slug=course.slug)
    else:
        form = LessonForm(instance=lesson)

    return render(request, 'instructors/edit_lesson.html', {'form': form, 'lesson': lesson, 'course': course})


@login_required
def delete_course(request, slug):
    course = get_object_or_404(Course, slug=slug, instructor=request.user)

    if request.method == "POST":
        course.delete()
        messages.success(request, "Course deleted successfully!")
        return redirect("courses:home")

    return render(request, "instructors/delete_course.html", {"course": course})
