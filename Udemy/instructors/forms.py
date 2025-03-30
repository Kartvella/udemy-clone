from django import forms
from courses.models import Course, Lesson

class CourseCreateForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'price', 'topic', 'thumbnail', 'level']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None) 
        super().__init__(*args, **kwargs)

        if user:
            self.user = user

    def save(self, commit=True):
        course = super().save(commit=False)
        if hasattr(self, 'user'):
            course.instructor = self.user
        if commit:
            course.save()
        return course


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'description', 'video', 'order']
        # widgets = {
        #     'description': forms.Textarea(attrs={'rows': 4}),
        #     'video': forms.ClearableFileInput(attrs={'accept': 'video/*'}),
        # }

    # def save(self, commit=False):

    #     lesson = super().save(commit=False)

    #     self.course = lesson.course

    #     super().save()