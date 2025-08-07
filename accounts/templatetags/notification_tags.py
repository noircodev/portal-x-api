from django import template
from ..models import Notification
from django.http import HttpRequest
register = template.Library()


@register.inclusion_tag('account/snippets/notification_snippet.html', takes_context=True)
def get_notification(context):
    request: HttpRequest = context.get('request')
    user = request.user

    notification = Notification.objects.filter(user=user, read=False)
    return {
        'notifications': notification,
        'has_notification': notification.exists(),
    }
