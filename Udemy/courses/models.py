from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField
from django.utils.text import slugify


class Topic(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True, blank=True,
                            help_text="""Slug for a topic.
                            If not provided, default will be slugified name""")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Course(models.Model):

    BEGGINER = 'beginner'
    INTERMEDIATE = 'intermediate'
    ADVANCED = 'advanced'

    LEVEL_CHOICES = {
        BEGGINER: 'Beginner',
        INTERMEDIATE: 'Intermediate',
        ADVANCED: 'Advanced'
    }
    
    instructor = models.ForeignKey(User, related_name='courses', on_delete=models.CASCADE)
    title = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True, blank=True,
                            help_text="""Slug for a course.
                            If not provided, default will be slugified title""")
    description = models.TextField()
    price = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    topic = models.ForeignKey(Topic, related_name='courses', on_delete=models.CASCADE,)
    thumbnail = CloudinaryField('image', blank=True, null=True)
    students = models.ManyToManyField(User, through='Enrollment')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    level = models.CharField(max_length=12, choices=LEVEL_CHOICES, default=BEGGINER)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def rating(self):
        return self.reviews.aggregate(avg_rating=models.Avg('rating'))['avg_rating'] or 0

    @property
    def total_reviews(self):
        return self.reviews.count()
    
    def get_top_courses_by_topic(topic):
        return Course.objects.filter(topic=topic).annotate(avg_rating=models.Avg('reviews__rating')).order_by('-avg_rating')[:3]
    
    def __str__(self):
        return self.title
    

class Lesson(models.Model):
    course = models.ForeignKey(Course, related_name='lessons', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True,
                            help_text="""Slug for a course.
                            If not provided, default will be slugified title""")
    video = CloudinaryField(resource_type='video', blank=False, null=False)
    description = models.TextField(blank=True, null=True)
    order = models.IntegerField(default=0)
    # duration = models.PositiveIntegerField(help_text="Duration in seconds", default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class Review(models.Model):
    course = models.ForeignKey(Course, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(choices=[(1, '1 Star'), (2, '2 Stars'), (3, '3 Stars'), (4, '4 Stars'), (5, '5 Stars')])
    review_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.username} for {self.course.title}"
    
    class Meta:
        unique_together = ('user', 'course')

class Enrollment(models.Model):
    user = models.ForeignKey(User, related_name='enrollments', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name='enrollments', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    # progress = models.FloatField(default=0.0, help_text="Percentage of course completed")

    def __str__(self):
        return f"{self.user.username} enrolled in {self.course.title}"

