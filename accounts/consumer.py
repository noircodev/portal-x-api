from django.utils.text import Truncator
from django.contrib.sites.models import Site
from accounts.signals import (email_confirmed, user_signed_up, email_changed)
from accounts.models import (
    Account, AccountEmail,)
from django.dispatch import receiver
from django.contrib.auth.models import User
from task.email.mailer import (
    send_reply_received_email, send_confirmation_email)


@receiver(user_signed_up)
def social_auth_signup_signal_handler(user: User, request, **kwargs):
    site = Site.objects.get_current()
    account_pref, _ = AccountEmail.objects.get_or_create(user=user,
                                                         email=user.email,

                                                         )
    account, _ = Account.objects.get_or_create(user=user)
    Account.objects.filter(pk=account.pk).update(account_pref=account_pref)
    send_confirmation_email(request, user.email, is_welcome_email=True)


@receiver(email_confirmed)
def process_email_confirmation(request, user, **kwargs):
    AccountEmail.objects.filter(user=user).update(verified=True)


@receiver(email_changed)
def email_changed_signal_handler(sender: User, request, user, new_email,  **kwargs):
    AccountEmail.objects.filter(user=user).update(verified=False)
    send_confirmation_email(request, new_email, is_welcome_email=False)
