from django.shortcuts import render, get_object_or_404, redirect
from .models import Course, Lesson, Review, Topic
from django.db.models import Avg, Q



def home(request):
    query = request.GET.get('q', '').strip()

    # Base QuerySet for courses (filtering only if there's a search query)
    courses = Course.objects.filter(
        Q(title__icontains=query) | Q(description__icontains=query)
    ) if query else Course.objects.all()

    # Fetch all topics
    topics = Topic.objects.all()

    # Get top 3 courses per topic (filtered by search query)
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
    context = {'course': course}

    return render(request, 'courses/course_detail.html', context)

def course_lesson(request, course_slug, lesson_slug):
    lesson = get_object_or_404(Lesson, slug=lesson_slug, course__slug=course_slug)
    context = {'lesson': lesson}
    return render(request, 'courses/course_lesson.html', context)




    
