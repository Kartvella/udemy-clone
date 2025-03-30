from django.contrib import admin
from .models import Topic, Course, Lesson, Review, Enrollment

class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1 

class CourseAdmin(admin.ModelAdmin):
    inlines = [LessonInline]
    list_display = ['title', 'instructor', 'topic', 'price', 'created_at']
    search_fields = ['name', 'description']
    list_filter = ['topic']

class ReviewAdmin(admin.ModelAdmin):
    list_display = ['course', 'user', 'rating', 'created_at']
    list_filter = ['course', 'rating']
    search_fields = ['user__username', 'course__name']

admin.site.register(Topic)
admin.site.register(Course, CourseAdmin)
admin.site.register(Lesson)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Enrollment)
