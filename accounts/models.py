from django.utils.text import Truncator
from django.db.models import Count
from django.shortcuts import (reverse)
from django.utils.crypto import get_random_string
from django.db import models
from django.contrib.auth.models import User
from accounts.utils.country import (COUNTRY_CHOICES)
from accounts.utils.choices import (LANGUAGE_CHOICES)
from accounts.utils.helper_func import (account_image_upload_path)


class AccountEmail(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="account_email")
    email = models.EmailField(max_length=100)
    reply = models.BooleanField(default=True)
    product_update = models.BooleanField(default=False)
    special_offer = models.BooleanField(default=False)
    newsletter = models.BooleanField(default=False)
    review_request = models.BooleanField(default=False)
    survey = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.user.email})"


class SocialMethod(models.Model):
    SOCIAL_PROVIDER_CHOICES = (
        ('google', "Google"),
        ('twitter', "X (Formerly Twitter)"),
        ('github', "Github"),
        ('facebook', "Facebook"),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    active = models.BooleanField(default=False)
    social_provider = models.CharField(
        max_length=20, choices=SOCIAL_PROVIDER_CHOICES)
    date_disconnected = models.DateTimeField(blank=True, null=True)
    date_connected = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_social_provider_display()}"


class Account(models.Model):
    ACCOUNT_TYPE_CHOICES = (
        ('reviewer', "Reviewer"),
        ('provider', "Provider"),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    account_pref = models.OneToOneField(
        'AccountEmail', on_delete=models.SET_NULL, blank=True, null=True)
    profile_image = models.FileField(
        upload_to=account_image_upload_path, blank=True, null=True)
    account_type = models.CharField(
        max_length=50, default='reviewer', choices=ACCOUNT_TYPE_CHOICES)
    country = models.CharField(
        max_length=200, choices=COUNTRY_CHOICES, blank=True, null=True)
    timezone = models.CharField(
        max_length=100, default="UTC",)
    social_methods = models.ManyToManyField(
        SocialMethod, blank=True, related_name="accounts")
    active = models.BooleanField(default=True)

    @property
    def google_auth_enabled(self) -> bool:
        return SocialMethod.objects.filter(user=self.user, active=True, social_provider='google').exists()

    @property
    def github_auth_enabled(self) -> bool:
        return SocialMethod.objects.filter(user=self.user, active=True, social_provider='github').exists()

    @property
    def get_profile_image(self):
        if self.profile_image:
            pass
            return self.profile_image.url
        return '/static/dash/assets/images/user/default-avatar-profile-icon.jpg'

    def __str__(self):
        return f"{self.user.get_full_name()} - ({self.user.username})"


class Notification(models.Model):
    class Meta:
        ordering = ['-timestamp']
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    preview_title = models.CharField(max_length=200)
    heading = models.CharField(max_length=100)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    notification_link = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.preview_title

    def get_absolute_url(self):
        return reverse('dash:notification_read', kwargs={
            'slug': self.notification_link
        })

    def save(self, *args, **kwargs):
        if self.notification_link == None:
            self.notification_link = get_random_string(35)
        super(Notification, self).save(*args, **kwargs)
