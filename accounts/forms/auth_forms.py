from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth import password_validation
from task.email.mailer import send_confirmation_email
from django.db.models import Q
from django import forms
from django.http import HttpRequest
from accounts.models import (AccountEmail, Account, Notification, SocialMethod,
                             )
from accounts.signals import (email_changed)


class EmailSubscribtionTypeForm(forms.ModelForm):
    form_messages = {
        "update_success": "Email preferences updated successfully"
    }

    class Meta:
        model = AccountEmail
        fields = ['reply', 'product_update', 'special_offer',
                  'newsletter', 'review_request', 'survey']

    def __init__(self, request: HttpRequest, *args, **kwargs):
        self.user = request.user
        self.message = None
        self.pref, self.pref_created = AccountEmail.objects.get_or_create(
            user=self.user)
        self.request = request
        super().__init__(*args, **kwargs)

    def update(self):
        AccountEmail.objects.filter(
            pk=self.pref.pk).update(**self.cleaned_data)
        if self.pref_created:
            Account.objects.filter(user=self.user).update(
                account_pref=self.pref)
        self.message = self.form_messages['update_success']
        return self.pref


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(max_length=50, )
    password1 = forms.CharField(max_length=50, )
    password2 = forms.CharField(max_length=50, )

    def __init__(self, request: HttpRequest, *args, **kwargs):
        self.user = request.user
        super().__init__(*args, **kwargs)

    error_messages = {
        "invalid_old_password": ("Invalid old password, please enter your current password"),
        "password_mismatch": ("Password mismatch, please re-type same password"),
        "old_password_reused": ("New password cannot be same as old password"),
    }

    def clean(self):
        cleaned_data = super().clean()
        old_password = cleaned_data.get('old_password')
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        # Validate user password

        if not self.user.check_password(old_password):
            raise ValidationError(
                self.error_messages["invalid_old_password"],
                code="invalid_old_password",
            )
        if password1 != password2:
            raise ValidationError(
                self.error_messages["password_mismatch"],
                code="password_mismatch",
            )
        if self.user.check_password(password2):
            raise ValidationError(
                self.error_messages["old_password_reused"],
                code="old_password_reused",
            )
        password_validation.validate_password(password1, self.user)
        return cleaned_data

    def save(self, commit=True):
        new_password = self.cleaned_data.get('password2')
        self.user.set_password(new_password)
        if commit:
            self.user.save()
        return self.user


class UpdateProfileForm(forms.ModelForm):
    first_name = forms.CharField()
    last_name = forms.CharField()

    class Meta:
        model = Account
        fields = ['country', 'timezone', ]

    def __init__(self, request: HttpRequest, *args, **kwargs) -> None:
        self.user = request.user
        self.account = Account.objects.filter(user=self.user)
        super().__init__(*args, **kwargs)

    def update(self):
        first_name = self.cleaned_data.pop('first_name')
        last_name = self.cleaned_data.pop('last_name')
        User.objects.filter(username=self.user.username).update(first_name=first_name,
                                                                last_name=last_name
                                                                )
        self.account.update(**self.cleaned_data)
        return self.user


class NotificationForm(forms.Form):
    event_id = forms.IntegerField(required=False)

    def __init__(self, request,  *args, **kwargs):
        self.user = request.user
        super().__init__(*args, **kwargs)

    def delete(self):
        event_id = self.cleaned_data.get('event_id')
        Notification.objects.get(id=event_id, user=self.user).delete()

    def clear_all(self):
        Notification.objects.filter(user=self.user).delete()


class EmailUpdateForm(forms.Form):
    email = forms.EmailField()
    error_messages = {
        'email_exists': ("A user with this email address already exists"),
    }

    def __init__(self, request: HttpRequest, *args, **kwargs):
        self.user = request.user
        self.request = request
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        user = User.objects.filter(
            Q(email__iexact=email,) & ~Q(pk=self.user.id))
        if user.exists():
            raise ValidationError(self.error_messages['email_exists'],
                                  code="email_exists")
        return email

    @property
    def email_changed(self) -> bool:
        email = self.cleaned_data.get('email')
        return not User.objects.filter(email__iexact=email, username=self.user.username).exists()

    def update(self):
        email = self.cleaned_data.get('email')
        if self.email_changed:
            User.objects.filter(id=self.user.id).update(email=email)
            email_changed.send(User, request=self.request,  user=self.user, new_email=email,
                               ** self.cleaned_data)
        return self.user


class EmailVerificationForm(forms.Form):
    email = forms.EmailField()

    def __init__(self, request: HttpRequest, *args, **kwargs):
        self.user = request.user
        self.request = request
        self.message = None
        super().__init__(*args, **kwargs)

    def send_verification(self):
        new_email = self.cleaned_data.get('email')
        send_confirmation_email(self.request, new_email)
        self.message = "Verification email sent"
        return self.user


class ChangeAccountImageForm(forms.Form):
    profile_image = forms.FileField()

    def __init__(self, request, *args, **kwargs):
        self.user = request.user
        self.account = Account.objects.get(user=self.user)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        image = cleaned_data.get('profile_image')
        if not image:
            raise ValidationError("Please select a valid image")

        return cleaned_data

    def save(self, commit=True):
        if commit:
            self.account.profile_image = self.cleaned_data.get('profile_image')
            self.account.save()
        return self.account


class DeleteAccountImageForm(forms.Form):

    def __init__(self, request, *args, **kwargs):
        self.user = request.user
        self.account = Account.objects.get(user=self.user)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        if commit:
            self.account.profile_image = None
            self.account.save()
        return self.account


class DeleteAccountForm(forms.Form):
    password = forms.CharField()

    def __init__(self, request, *args, **kwargs):
        self.user: User = request.user
        self.account = Account.objects.get(user=self.user)
        super().__init__(*args, **kwargs)

    error_messages = {
        "invalid_password": "The password you entered is incorrect",
    }

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not self.user.check_password(password):
            raise ValidationError(
                self.error_messages["invalid_password"],
                code="invalid_password",
            )
        return password

    def delete(self, ):
        self.user.is_active = False
        self.user.save()
        return self.account


class SocialConnectionForm(forms.Form):
    social_provider = forms.CharField()
    form_action = forms.CharField()

    error_messages = {
        'invalid_request': "You have initiated an invalid request",
    }
    success_messages = {
        'connected': "Social account successfully connected",
        'disconnected': "Social account successfully disconnected",
    }

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = request.user
        self.social_method = None
        self.message = None
        self.account = Account.objects.get(user=self.user)

    def clean(self):
        cleaned_data = super().clean()
        social_provider = cleaned_data.get('social_provider')
        form_action = cleaned_data.get('form_action')
        if not (social_provider and form_action):
            raise ValidationError(
                self.error_messages['invalid_request'], code='invalid_request')
        if social_provider not in ['google', 'github']:
            raise ValidationError(
                self.error_messages['invalid_request'], code='invalid_request')
        self.social_provider = social_provider
        self.form_action = form_action
        return cleaned_data

    def update(self, ):
        self.social_method, created = SocialMethod.objects.get_or_create(
            user=self.user,
            social_provider=self.social_provider,
        )
        if created:
            SocialMethod.objects.filter(
                pk=self.social_method.pk).update(active=True)
            self.message = self.success_messages['connected']
            return self.social_method
        if self.form_action == 'connect':
            SocialMethod.objects.filter(
                pk=self.social_method.pk).update(active=True)
            self.message = self.success_messages['connected']
            return self.social_method
        if self.form_action == 'disconnect':
            SocialMethod.objects.filter(
                pk=self.social_method.pk).update(active=False)
            self.message = self.success_messages['disconnected']

            return self.social_method


class NotificationForm(forms.Form):
    instance_id = forms.IntegerField()

    def __init__(self, request: HttpRequest, *args, **kwargs):
        self.request = request
        self.user = request.user
        super().__init__(*args, **kwargs)

    def delete(self):
        instance_id = self.cleaned_data.get('instance_id')
        Notification.objects.filter(user=self.user, id=instance_id).delete()


class SetUseablePasswordForm(forms.Form):
    password1 = forms.CharField(max_length=50, )
    password2 = forms.CharField(max_length=50, )

    def __init__(self, request: HttpRequest, *args, **kwargs):
        self.user = request.user
        super().__init__(*args, **kwargs)

    error_messages = {
        "password_mismatch": ("Password mismatch, please re-type same password"),
        "old_password_reused": ("New password cannot be same as old password"),
    }

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        # Validate user password

        if password1 != password2:
            raise ValidationError(
                self.error_messages["password_mismatch"],
                code="password_mismatch",
            )

        password_validation.validate_password(password1, self.user)
        return cleaned_data

    def save(self, commit=True):
        new_password = self.cleaned_data.get('password2')
        self.user.set_password(new_password)
        if commit:
            self.user.save()
        return self.user
