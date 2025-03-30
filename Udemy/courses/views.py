from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from .models import Course, Lesson, Review, Topic, Enrollment
from django.db.models import Avg, Q
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from courses.forms import ReviewForm


def home(request):
    query = request.GET.get('q', '').strip()

    courses = Course.objects.filter(
        Q(title__icontains=query) | Q(description__icontains=query)
    ) if query else Course.objects.all()

    topics = Topic.objects.all()

    top_courses_by_topic = {
        topic: Course.objects.filter(
            topic=topic
        ).filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        ).annotate(
            avg_rating=Avg('reviews__rating')
        ).order_by('-avg_rating')[:3]
        for topic in topics
    }

    context = {
        'courses': courses,
        'query': query,
        'top_courses_by_topic': top_courses_by_topic
    }
    return render(request, 'courses/index.html', context)


def course_detail(request, slug):
    course = get_object_or_404(Course, slug=slug)

    # Check if the user is enrolled in the course
    is_enrolled = Enrollment.objects.filter(user=request.user, course=course).exists() if request.user.is_authenticated else False
    
    # Check if the user has already reviewed the course
    has_reviewed = Review.objects.filter(user=request.user, course=course).exists() if request.user.is_authenticated else False
    
    # Check if the user is the instructor of the course
    is_instructor = course.instructor == request.user

    context = {
        'course': course,
        'is_enrolled': is_enrolled,
        'has_reviewed': has_reviewed,
        'is_instructor': is_instructor,  # Add this to the context
    }

    return render(request, 'courses/course_detail.html', context)


@login_required
def course_lesson(request, course_slug, lesson_slug):
    lesson = get_object_or_404(Lesson, course__slug=course_slug, slug=lesson_slug)
    
    if not request.user.has_perm('courses.view_lesson'):
        return HttpResponse("you don't have permission to access lessons")

    return render(request, "courses/course_lesson.html", {"lesson": lesson})



@login_required
def add_review(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk)
    
    # Check if user is enrolled in the course
    is_enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()
    if not is_enrolled:
        messages.error(request, "You must be enrolled in the course to leave a review.")
        return redirect("courses:course_detail", slug=course.slug)

    # Prevent users from reviewing the same course multiple times
    existing_review = Review.objects.filter(user=request.user, course=course).first()
    if existing_review:
        messages.error(request, "You have already reviewed this course.")
        return redirect("courses:course_detail", slug=course.slug)

    if request.method == "POST":
        rating = request.POST.get("rating")
        review_text = request.POST.get("review_text")

        # Create a new review and associate it with the user and the course
        review = Review(user=request.user, course=course, rating=rating, review_text=review_text)
        review.save()
        
        messages.success(request, "Your review has been submitted successfully!")
        return redirect("courses:course_detail", slug=course.slug)

    # If the method is not POST, we don't need to return a separate view, just redirect
    return redirect("courses:course_detail", slug=course.slug)


def courses(request):
    courses = Course.objects.select_related('topic')
    topics = Topic.objects.all()  # Fetch all topics for the dropdown
    
    if (topic := request.GET.get('topic')):
        courses = courses.filter(topic=topic)

    context = {'courses': courses, 'topics': topics}

    return render(request, 'courses/courses.html', context)
