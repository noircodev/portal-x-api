from accounts.views.auth_views import *
from accounts.views.account_views import *
from accounts.views.profile_views import *


# Authentication Views

account_login_view = AccountLoginView.as_view()
account_signup_view = SignupView.as_view()
account_logout_view = LogoutView.as_view()
account_password_reset_view = AccountPasswordResetView.as_view()
account_password_reset_done_view = AccountPasswordResetDoneView.as_view()
account_password_reset_complete_view = AccountPasswordResetCompleteView.as_view()
account_password_reset_confirm_view = AccountPasswordResetConfirmView.as_view()
account_email_verify_view = AccountEmailVerifyView.as_view()
# profile settings
account_profile_settings_view = AccountSettingsView.as_view()
account_notifications_view = AccountNotificationView.as_view()
# User account views
index_view = IndexView.as_view()
add_search_keywords_view = AddEventFileUploadView.as_view()
event_list_view = EventListView.as_view()
zip_code_view = ZipCodeView.as_view()
search_keyword_view = SearchKeywordsView.as_view()
beta_subscriber_view = BetaSubscriberView.as_view()

page_protected_view = PageProtectedView.as_view()

add_event_view = AddEventView.as_view()

# add_organization_view = AddOrganizationView.as_view()
# index_view = IndexView.as_view()
# index_view = IndexView.as_view()
# index_view = IndexView.as_view()
