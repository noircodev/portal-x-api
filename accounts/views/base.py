# from dash.utils.helper_func import (verify_email)
from accounts.utils.tokens import email_token_generator
from accounts.utils import choices
from django.contrib.auth.views import (
    LoginView, PasswordResetView, PasswordResetCompleteView, PasswordResetConfirmView, PasswordResetDoneView)
from django.views.generic import View
from django.http import (HttpResponseForbidden, HttpRequest)
from django.contrib import messages
from django.contrib.auth import (
    logout, login, authenticate, update_session_auth_hash)
from accounts.account_forms import (LoginForm, UserCreationForm)
from django.shortcuts import (render, redirect, resolve_url, get_object_or_404)
from django.conf import settings
from django.urls import reverse_lazy
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.mixins import (LoginRequiredMixin)
from django.contrib.auth.models import (User)
from django.utils import timezone
import pytz
# User dashboard
from accounts.forms import (EmailSubscribtionTypeForm, ChangePasswordForm, UpdateProfileForm,
                            EmailUpdateForm, ChangeAccountImageForm, DeleteAccountImageForm, SocialConnectionForm,
                            DeleteAccountForm, EmailVerificationForm, NotificationForm, SetUseablePasswordForm,

                            )
from accounts.models import (Notification)
# utils app import
from task.utils.helper_func import (get_error_message_text, get_error_messages, paginate_queryset)

# event app import
from event.models import (Event, SearchPhrase, Location, BetaSubscriber, City)
from event.forms import (EventSearchForm)


# account forms import
from accounts.forms import (
    SearchKeywordForm, UpdateSearchKeywordForm,
    EventForm,
)
