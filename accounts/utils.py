import random
from django.utils import timezone
from django.core.cache import cache
from django.template.loader import render_to_string
from django.core.mail import EmailMessage


def human_readable_time_ago(timestamp):
    """
    Returns human readable difference between now and given timestamp
    """
    if not timestamp:
        return "Never active"

    now = timezone.now()
    diff = now - timestamp
    seconds = int(diff.total_seconds())

    if seconds < 60:
        return f"{seconds} sec ago"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes} min ago"
    hours = minutes // 60
    if hours < 24:
        return f"{hours} hr ago"
    days = hours // 24
    if days < 30:
        return f"{days} day ago"
    months = days // 30
    if months < 12:
        return f"{months} month ago"
    years = months // 12
    return f"{years} year ago"


def generate_otp():
    return str(random.randint(100000, 999999))


def send_otp_email(email):
    otp = generate_otp()

    cache.set(f"pwd_reset_otp_{email}", otp, timeout=300)

    subject = "🔒 Verify Your Account"

    html_content = render_to_string("emails/verify_email.html", {"OTP": otp})

    email = EmailMessage(
        subject=subject,
        body=html_content,
        to=[email],
    )
    email.content_subtype = "html"
    email.send()
