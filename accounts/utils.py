import random
from django.utils import timezone

from django.utils import timezone
from datetime import timedelta


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
