from django.utils.crypto import get_random_string
from django.conf import settings

GUEST_COOKIE_NAME = getattr(
    settings, 'GUEST_COOKIE_NAME', '_guest_user_cookies')
# 1 year in seconds (31536000 seconds)
GUEST_COOKIE_MAX_AGE = 365 * 24 * 60 * 60


class SetGuestUserCookiesMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Check if cookie is missing in both request and response
        if (GUEST_COOKIE_NAME not in request.COOKIES and
                GUEST_COOKIE_NAME not in response.cookies):
            cookie_value = get_random_string(50)
            response.set_cookie(
                GUEST_COOKIE_NAME,
                cookie_value,
                max_age=GUEST_COOKIE_MAX_AGE,
                httponly=True,
                secure=getattr(settings, 'SESSION_COOKIE_SECURE', False),
                samesite=getattr(settings, 'SESSION_COOKIE_SAMESITE', 'Lax'),
            )
        return response
