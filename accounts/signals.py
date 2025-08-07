
from django import dispatch


user_signed_up = dispatch.Signal()

email_confirmed = dispatch.Signal()
social_authentication = dispatch.Signal()
social_auth_signup = dispatch.Signal()
social_auth_signin = dispatch.Signal()
user_logged_in = dispatch.Signal()
user_logged_out = dispatch.Signal()
password_set = dispatch.Signal()
password_changed = dispatch.Signal()
password_reset = dispatch.Signal()
email_confirmation_sent = dispatch.Signal()
email_changed = dispatch.Signal()
email_added = dispatch.Signal()
email_removed = dispatch.Signal()
