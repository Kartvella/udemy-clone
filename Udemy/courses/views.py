from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from .models import Course, Lesson, Review, Topic, Enrollment
from django.db.models import Avg, Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages


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

    is_enrolled = Enrollment.objects.filter(user=request.user, course=course).exists() if request.user.is_authenticated else False
    
    has_reviewed = Review.objects.filter(user=request.user, course=course).exists() if request.user.is_authenticated else False
    
    is_instructor = course.instructor == request.user

    context = {
        'course': course,
        'is_enrolled': is_enrolled,
        'has_reviewed': has_reviewed,
        'is_instructor': is_instructor,
    }

    return render(request, 'courses/course_detail.html', context)


@login_required
def course_lesson(request, course_slug, lesson_slug):
    lesson = get_object_or_404(Lesson, course__slug=course_slug, slug=lesson_slug)

    if not request.user.has_perm('courses.view_lesson'):
        return HttpResponse("You don't have permission to access lessons")

    previous_lesson = Lesson.objects.filter(course=lesson.course, order__lt=lesson.order).order_by('-order').first()
    next_lesson = Lesson.objects.filter(course=lesson.course, order__gt=lesson.order).order_by('order').first()

    return render(request, "courses/course_lesson.html", {
        "lesson": lesson,
        "previous_lesson": previous_lesson,
        "next_lesson": next_lesson
    })


@login_required
def add_review(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk)
    
    is_enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()
    if not is_enrolled:
        messages.error(request, "You must be enrolled in the course to leave a review.")
        return redirect("courses:course_detail", slug=course.slug)

    existing_review = Review.objects.filter(user=request.user, course=course).first()
    if existing_review:
        messages.error(request, "You have already reviewed this course.")
        return redirect("courses:course_detail", slug=course.slug)

    if request.method == "POST":
        rating = request.POST.get("rating")
        review_text = request.POST.get("review_text")

        review = Review(user=request.user, course=course, rating=rating, review_text=review_text)
        review.save()
        
        messages.success(request, "Your review has been submitted successfully!")
        return redirect("courses:course_detail", slug=course.slug)

    return redirect("courses:course_detail", slug=course.slug)


def courses(request):
    courses = Course.objects.select_related('topic')
    topics = Topic.objects.all()
    
    if (topic := request.GET.get('topic')):
        courses = courses.filter(topic=topic)

    context = {'courses': courses, 'topics': topics}

    return render(request, 'courses/courses.html', context)
