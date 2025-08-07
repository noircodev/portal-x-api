from django.utils.translation import gettext_lazy as _
import requests
from django.utils.crypto import get_random_string
from accounts.signals import (user_signed_up, email_changed)
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django import forms
from django.contrib.auth import (password_validation, authenticate)
from django.conf import settings
from . import app_settings


class LoginForm(forms.Form):
    login = forms.CharField(max_length=50)
    password = forms.CharField(max_length=50)

    error_messages = {
        "login_mismatch": ("The username or password you entered is incorrect"),
        "account_inactive": ("Your account has been suspended, please contact us"),
    }

    def __init__(self, request=None, *args, **kwargs):
        self.user = None
        self.request = request
        self.is_active_user = False
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("login")
        password = cleaned_data.get("password")
        if password and username:
            self.user = authenticate(
                self.request, username=username, password=password)
            if self.user:
                self.user_can_login(self.user)
            else:
                self.get_login_error()
        return cleaned_data

    def user_can_login(self, user):
        can_login = False
        if user.is_active:
            can_login = True
        self.is_active_user = can_login
        return self.is_active_user

    def get_login_error(self):
        if self.user and not self.user.is_active:
            raise ValidationError(
                self.error_messages["account_inactive"],
                code="account_inactive",
            )
        else:
            raise ValidationError(
                self.error_messages["login_mismatch"],
                code="login_mismatch",
            )

    def get_user(self):
        return self.user


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(max_length=50, )
    password1 = forms.CharField(max_length=50, )
    password2 = forms.CharField(max_length=50, )

    def __init__(self, request, *args, **kwargs):
        self.user = request.user
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        old_password = cleaned_data.get('old_password')
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        # Validate user password

        if not self.user.check_password(old_password):
            raise ValidationError(
                "Invalid old password, please enter your current password")
        if password1 != password2:
            raise ValidationError(
                "Password mismatch, please re-type same password")
        if self.user.check_password(password2):
            raise ValidationError(
                "New password cannot be same as old password")
        password_validation.validate_password(password1, self.user)
        return cleaned_data

    def save(self, commit=True):
        new_password = self.cleaned_data.get('password2')
        self.user.set_password(new_password)
        if commit:
            self.user.save()
        return self.user


class UserCreationForm(forms.ModelForm):
    """
    A form that creates a user with no privileges, from the given username and password.
    """
    password = forms.CharField(
        widget=forms.PasswordInput,
        error_messages={"required": _("Password is required.")},
    )
    account_type = forms.CharField(required=False)

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]

    error_messages = {
        "password_mismatch": _("The two password fields didn’t match."),
        "user_exists": _("A user with this username already exists."),
        "email_exists": _("A user with this email already exists."),
        "password_required": _("The password field is required."),
        "username_required": _("The username field is required."),
        "email_required": _("The email field is required."),
        "username_blacklist": _("You are not allowed to sign up with this username."),
        "bot_challenge_failed": _("We couldn't verify you are human."),
    }

    def __init__(self, request, cf_turnstile_response, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.cf_turnstile_response = cf_turnstile_response
        self.TURNSTILE_SECRET = app_settings.CLOUDFLARE_TURNSTILE_SECRET_KEY
        self.SITE_VERIFY = app_settings.VERIFICATION_URL

    def clean(self):
        cleaned_data = super().clean()
        if not self._is_valid_bot_challenge():
            raise ValidationError(
                self.error_messages["bot_challenge_failed"], code="bot_challenge_failed"
            )
        return cleaned_data

    def clean_username(self):
        username = self.cleaned_data.get("username", "").strip()

        if not username:
            self._raise_validation_error("username_required")

        if self._meta.model.objects.filter(username__iexact=username).exists():
            self._raise_validation_error("user_exists")

        if self._is_username_blacklisted(username):
            self._raise_validation_error("username_blacklist")

        return username

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip().lower()

        if not email:
            self._raise_validation_error("email_required")

        if self._meta.model.objects.filter(email__iexact=email).exists():
            self._raise_validation_error("email_exists")

        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
            if hasattr(self, "save_m2m"):
                self.save_m2m()
        user_signed_up.send(
            sender=User, user=user, request=self.request, **self.cleaned_data
        )
        return user

    def _is_valid_bot_challenge(self):
        """Validate bot challenge using Turnstile."""
        if not self.cf_turnstile_response:
            return False

        try:
            data = {"secret": self.TURNSTILE_SECRET,
                    "response": self.cf_turnstile_response}
            response = requests.post(self.SITE_VERIFY, data=data)
            result = response.json()
            return result.get("success", False)
        except requests.RequestException:
            return False

    def _is_username_blacklisted(self, username):
        """Check if the username is blacklisted."""
        blacklist = getattr(settings, "ACCOUNT_USERNAME_BLACKLIST", [])
        return any(name.lower() == username.lower() for name in blacklist)

    def _raise_validation_error(self, error_key):
        """Helper to raise a validation error with a specific error message."""
        raise ValidationError(self.error_messages[error_key], code=error_key)
