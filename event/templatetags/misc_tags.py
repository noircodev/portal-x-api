from django.http import HttpRequest
from django.conf import settings
from event.models import RecentSearch
import datetime
from django import template

register = template.Library()


@register.filter
def is_today(value):
    """Checks if the given date is today"""
    if isinstance(value, datetime.date):
        return value == datetime.date.today()
    return False


@register.inclusion_tag('home/includes/recent_search.html', takes_context=True)
def get_recent_searches(context):
    request: HttpRequest = context.get('request')
    GUEST_COOKIE_NAME = getattr(
        settings, 'GUEST_COOKIE_NAME', '_guest_user_cookies')
    recent_search = []
    cookies_id = request.COOKIES.get(GUEST_COOKIE_NAME)
    if cookies_id:
        recent_search = RecentSearch.objects.filter(cookies_id=cookies_id)[:10]

    return {
        'recent_searches': recent_search,
    }
