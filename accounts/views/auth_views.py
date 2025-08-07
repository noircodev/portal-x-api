from accounts.views.base import *


class LogoutView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponseForbidden("<h1> Method Not Allowed </h1>")

    def post(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, "Successfully logged out")
        return redirect(settings.ACCOUNT_LOGOUT_REDIRECT_URL)


class SignupView(View):
    def get(self, request: HttpRequest, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(settings.LOGIN_REDIRECT_URL)
        context = {

        }
        return render(request, "auth/signup.html", context)

    def post(self, request: HttpRequest, *args, **kwargs):
        cf_turnstile_response = request.POST.get('cf-turnstile-response')
        form = UserCreationForm(request, cf_turnstile_response, request.POST)
        if form.is_valid():
            user = form.save()
            # log user in
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect(settings.ACCOUNT_SIGNUP_REDIRECT_URL)
        context = {
            'form': form,
        }
        return render(request, 'auth/signup.html', context)


class AccountLoginView(LoginView):
    template_name = 'auth/login.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def get_default_redirect_url(self):
        """Return the default redirect URL."""
        redirect_to = self.request.POST.get('next_page')
        if redirect_to:
            return resolve_url(redirect_to)
        else:
            return resolve_url(settings.LOGIN_REDIRECT_URL)


class AccountPasswordResetView(PasswordResetView):
    template_name = 'auth/forgot_password.html'
    success_url = reverse_lazy("account_password_reset_done")
    email_template_name = 'email/auth/password_reset_email.html'
    html_email_template_name = 'email/auth/password_reset_email.html'


class AccountPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'auth/password_reset_done.html'


class AccountPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'auth/password_reset_complete.html'


class AccountPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'auth/confirm_password_reset.html'
    success_url = reverse_lazy("account_password_reset_complete")


class AccountEmailVerifyView(View):
    def get(self, request, *args, **kwargs):
        uid = kwargs.get('uidb64')
        token = kwargs.get('token')
        context = {
            'valid_link': False,
        }
        if uid and token:
            user = email_token_generator.get_user(uid)
            valid_token = email_token_generator.check_token(user, token)
            if valid_token:
                from accounts.signals import (email_confirmed)
                email_confirmed.send(sender=User, user=user,
                                     request=self.request,  *args, **kwargs)

                context.update(
                    valid_link=True,
                )
        return render(request, 'auth/verify_email.html', context)


class ProfileSettingsView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest, *args, **kwargs):
        keyword = SearchPhrase.objects.all()
        context = {
            "keywords": keyword,

        }
        return render(request, 'account/user/account_settings.html', context)

    def post(self, request: HttpRequest, *args, **kwargs):
        action = request.POST.get('action')
        if action == 'update_keyword':
            form = UpdateSearchKeywordForm(request, request.POST)
            if form.is_valid():
                form.update()
                messages.success(
                    request, "Search keywords updated successfully.")
                return redirect('account_search_keywords')
        elif action == 'delete_keyword':
            form = UpdateSearchKeywordForm(request, request.POST)
            if form.is_valid():
                form.delete()
                messages.success(
                    request, "Search keywords deleted successfully.")
                return redirect('account_search_keywords')

        get_error_messages(request, form.errors)
        return redirect(request.META.get('HTTP_REFERER', 'account_review'))
