from django.contrib.sites.shortcuts import get_current_site
from task.tokens import email_token_generator
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings


def send_reply_received_email(request, review, reply, recipient_email,):
    if request.is_secure():
        protocol = "https"
    else:
        protocol = "http"
    current_site = get_current_site(request)

    context = {
        'protocol': protocol,
        'email': recipient_email,
        'domain': current_site.domain,
        'site_name': current_site.name,
        'review': review,
        'reply': reply,

    }
    subject = "Someone Responded to Your Review"
    html_template = render_to_string('mail/reply_received.html', context)
    plain_message = strip_tags(html_template)
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient = [recipient_email]
    return send_mail(subject, plain_message, from_email, recipient, html_message=html_template)


def notify_admin(subject, message):
    """
    Send email to admin.
    """
    mail = EmailMessage(
        subject=subject,
        body=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[settings.DEFAULT_SUPPORT_EMAIL, ],
    )
    return mail.send()


def send_email_on_contact_receipt(context, customer_email,):
    """
    receipt of email
    Send email to user on message receptance
    """
    subject = "Acknowledging email Receptance"
    html_template = render_to_string('mail/message_received.html', context)
    plain_message = strip_tags(html_template)
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient = [customer_email]
    return send_mail(subject, plain_message, from_email, recipient, html_message=html_template)


def send_confirmation_email(request, recipient_email, is_welcome_email=False):
    token = email_token_generator.make_token(request.user, )
    if request.is_secure():
        protocol = "https"
    else:
        protocol = "http"
    current_site = get_current_site(request)

    context = {
        'token': token,
        'protocol': protocol,
        'is_welcome_email': is_welcome_email,
        'user': request.user,
        'email': recipient_email,
        'domain': current_site.domain,
        'site_name': current_site.name,
        'uid': email_token_generator.generate_uidb64(request.user.id),

    }
    if is_welcome_email:
        subject = "Welcome to VPS Advisor"
    else:
        subject = "Please Veify Your Email"
    html_template = render_to_string('mail/confirm_email.html', context)
    plain_message = strip_tags(html_template)
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient = [recipient_email]
    return send_mail(subject, plain_message, from_email, recipient, html_message=html_template)
