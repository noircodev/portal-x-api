from django.core.paginator import (Paginator, EmptyPage, PageNotAnInteger)
from django.contrib import messages
from django.http import HttpRequest
from django.conf import settings


GUEST_COOKIE = getattr(settings, 'GUEST_COOKIE_NAME', '_guest_user_cookies')


def get_error_message_text(form_errors):
    for error in form_errors:
        error_msg = form_errors.get(error).as_text().lstrip('* ')
        if error_msg != '__all__':
            return error_msg


def get_error_messages(request: HttpRequest,  form_errors):
    for error in form_errors:
        error_msg = form_errors.get(error).as_text().lstrip('* ')
        if error_msg != '__all__':
            messages.add_message(request, messages.ERROR, error_msg)


def get_client_ip(request: HttpRequest):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def paginate_queryset(request: HttpRequest, query_set: dict, per_page: int = 12,):
    page = request.GET.get('page')
    paginator = Paginator(query_set, per_page)
    try:
        paginated_queryset = paginator.page(page)
    except PageNotAnInteger:
        paginated_queryset = paginator.page(1)
    except EmptyPage:
        paginated_queryset = paginator.page(paginator.num_pages)
    return paginated_queryset
