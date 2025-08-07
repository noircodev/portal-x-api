from django.urls import path
from accounts.views import *

auth_urls = [
    path('signup/', account_signup_view, name='account_signup'),
    path('login/', account_login_view, name='account_login'),
    path('logout/', account_logout_view, name='account_logout'),
    path('forgot-password/', account_password_reset_view,
         name='account_reset_password'),
    path('password-reset-done/', account_password_reset_done_view,
         name='account_password_reset_done'),
    path('password-reset-complete/', account_password_reset_complete_view,
         name='account_password_reset_complete'),
    path('confirm-password-reset/<uidb64>/<token>/',
         account_password_reset_confirm_view, name='account_password_reset_confirm'),
    path('verify-email/<str:uidb64>/<str:token>/',
         account_email_verify_view, name='account_email_verify'),

    path('profile-settings/', account_profile_settings_view,
         name='account_profile_settings'),
    path('notifications/', account_notifications_view,
         name='account_notifications'),




]
