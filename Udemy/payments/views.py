import paypalrestsdk
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from courses.models import Course, Enrollment, Lesson
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.mail import send_mail
from django.conf import settings


def create_payment(request, course_id):
    
    if not (course := get_object_or_404(Course, id=course_id)):
        messages.error(request, "Course not found.")
        return redirect('courses:home')

    if request.user == course.instructor or course.price == 0:
        Enrollment.objects.get_or_create(user=request.user, course=course)
        messages.success(request, f"You are the instructor of {course.title}. You are automatically enrolled!")
        return redirect('courses:course_detail', slug=course.slug)


    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "redirect_urls": {
            "return_url": request.build_absolute_uri(reverse('payments:execute_payment', args=[course.id])),
            "cancel_url": request.build_absolute_uri(reverse('courses:course_detail', args=[course.slug])),
        },
        "transactions": [{
            "amount": {
                "total": str(course.price),
                "currency": "USD"
            },
            "description": course.title
        }]
    })

    if payment.create():
        approval_url = next(link.href for link in payment.links if link.rel == "approval_url")
        return redirect(approval_url)
    else:
        messages.error(request, "There was an issue creating your payment.")
        return redirect('courses:course_detail', slug=course.slug)



def assign_lesson_permissions(user, course):
    # Get all lessons for the given course
    lessons = Lesson.objects.filter(course=course)

    # Get "view_lesson" permission
    content_type = ContentType.objects.get_for_model(Lesson)
    permission = Permission.objects.get(codename="view_lesson", content_type=content_type)

    # Assign "view_lesson" permission to the user for each lesson
    for lesson in lessons:
        # You can add permission only once for each lesson
        if not user.has_perm("courses.view_lesson", lesson):
            user.user_permissions.add(permission)



@csrf_exempt
def execute_payment(request, course_id):
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        messages.error(request, "Course not found.")
        return redirect("courses:home")

    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')

    if not payment_id or not payer_id:
        messages.error(request, "Invalid payment details. Please try again.")
        return redirect("courses:course_detail", slug=course.slug)

    payment = paypalrestsdk.Payment.find(payment_id)

    if payment.execute({"payer_id": payer_id}):
        enrollment, created = Enrollment.objects.get_or_create(user=request.user, course=course)

        if created:
            assign_lesson_permissions(request.user, course)

        send_mail(
            'Buy Course',
            f'{request.user.username} has successfully bought course: {course.title}',
            settings.DEFAULT_FROM_EMAIL,
            [request.user.email],
            fail_silently=False
        )
        messages.success(request, f"Payment successful! You are now enrolled in {course.title}.")
        return redirect("courses:course_detail", slug=course.slug)

    else:
        messages.error(request, f"Payment failed: {payment.error.get('message', 'Unknown error')}")
        return redirect("courses:course_detail", slug=course.slug)
