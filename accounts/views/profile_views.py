
from accounts.views.base import *


class AccountSettingsView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest, *args, **kwargs):
        timezone = pytz.common_timezones

        language = sorted(choices.LANGUAGE_CHOICES, key=lambda x: x[1])
        country = sorted(choices.COUNTRY_CHOICES, key=lambda x: x[1])
        context = {
            'countries': country,
            'common_timezones': timezone,
            'languages': language,

        }
        return render(request, 'account/user/account_settings.html', context)

    def post(self, request: HttpRequest, *args, **kwargs):
        action = request.POST.get('action')
        if action == "update_email_pref":
            form = EmailSubscribtionTypeForm(request, request.POST)
            if form.is_valid():
                form.update()
                messages.success(request, form.message)
                return redirect(request.META.get('HTTP_REFERER', 'account_home', ))
        elif action == 'update_password':
            form = ChangePasswordForm(request, request.POST)
            if form.is_valid():
                user = form.save()
                update_session_auth_hash(request, user)
                messages.success(
                    request, "Your password has been successfully updated")
                return redirect(request.META.get('HTTP_REFERER', 'account_home'))
            # Process profile update
        elif action == 'update_profile':
            form = UpdateProfileForm(request, request.POST)
            if form.is_valid():
                form.update()
                messages.success(
                    request, "Your profile has been successfully updated")
                return redirect(request.META.get('HTTP_REFERER', 'account_home'))
        elif action == 'update_email':
            form = EmailUpdateForm(request, request.POST)
            if form.is_valid():
                form.update()
                messages.success(
                    request, "Your email has been successfully updated")
                return redirect(request.META.get('HTTP_REFERER', 'account_home'))
        elif action == 'update_profile_image':
            form = ChangeAccountImageForm(
                request, request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, "Profile image successfully updated")
                return redirect(request.META.get('HTTP_REFERER', 'account_home'))
        elif action == 'delete_profile_image':
            form = DeleteAccountImageForm(
                request, request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, "Profile image successfully deleted")
                return redirect(request.META.get('HTTP_REFERER', 'account_home'))
        elif action == 'update_social_connection':
            form = SocialConnectionForm(request, request.POST, )
            if form.is_valid():
                form.update()
                messages.success(request, form.message)
                return redirect(request.META.get('HTTP_REFERER', 'account_home'))
        elif action == 'set_useable_password':
            form = SetUseablePasswordForm(request, request.POST, )
            if form.is_valid():
                form.save()
                messages.success(
                    request, "You can now log in using your new password.")
                update_session_auth_hash(request, request.user)

                return redirect(request.META.get('HTTP_REFERER', 'account_home'))

        elif action == 'resend_verification':
            form = EmailVerificationForm(request, request.POST, )
            if form.is_valid():
                form.send_verification()
                messages.success(request, form.message)
                return redirect(request.META.get('HTTP_REFERER', 'account_home'))
        elif action == 'delete_my_account':
            form = DeleteAccountForm(request, request.POST, )
            if form.is_valid():
                form.delete()
                messages.success(request, "Account deleted successfully")
                return redirect(request.META.get('home:home', '/'))
        get_error_messages(request, form.errors)
        return redirect(request.META.get('HTTP_REFERER', 'account_home'))


class AccountNotificationView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest, *args, **kwargs):
        notification = Notification.objects.filter(user=request.user)
        context = {
            'notifications': notification,

        }
        return render(request, 'account/user/notifications.html', context)

    def post(self, request: HttpRequest, *args, **kwargs):
        action = request.POST.get('action')
        if action == 'delete_notification':

            form = NotificationForm(request, request.POST)
            if form.is_valid():
                form.delete()
                messages.success(request, "Notification deleted successfully")
            return redirect(request.META.get('HTTP_REFERER', 'account_notifications'))
        get_error_messages(request, form.errors)
        return redirect(request.META.get('HTTP_REFERER', 'account_notifications'))
