from django.core.mail import send_mail
from django.conf import settings

def send_purchase_confirmation_email(user, book):
    subject = f"Purchase Confirmation: {book.title}"
    message = f"Dear {user.username},\n\nThank you for purchasing the book '{book.title}' by {book.author.user.username}.\n\nWe hope you enjoy reading it!"
    recipient_list = [user.email] 

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        recipient_list,
        fail_silently=False, 
    )