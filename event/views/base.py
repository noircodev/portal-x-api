from django.http import (HttpRequest, JsonResponse,
                         HttpResponsePermanentRedirect)
from django.contrib import messages
from django.shortcuts import render, redirect, reverse
from django.views.generic import (View, TemplateView)
from event.utils.helper_func import (paginate_queryset, get_error_messages)
from event.forms import (
    EventSearchForm, SearchSuggestionForm, SubmitEventForm, SubmitEventLinkForm, BetaSubscriberForm,
    MeilisearchSearchSuggestionForm)
from event.models import (RecentSearch, Event, Location)
from django.conf import settings
from django.utils import timezone

GUEST_COOKIE_NAME = getattr(
    settings, 'GUEST_COOKIE_NAME', '_guest_user_cookies')
