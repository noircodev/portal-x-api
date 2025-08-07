from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
import six
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes

UserModel = User()


class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    def get_user(self, uidb64):
        try:
            # urlsafe_base64_decode() decodes to bytestring
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (
            TypeError,
            ValueError,
            OverflowError,
            User.DoesNotExist,
            ValidationError,
        ):
            user = None
        return user

    def generate_uidb64(self, user_id):
        uuidb64_encoded = urlsafe_base64_encode(force_bytes(user_id))
        return uuidb64_encoded

    def _make_hash_value(self, user, timestamp):
        return (six.text_type(user.pk) + six.text_type(timestamp) + six.text_type(user.is_active))


email_token_generator = EmailVerificationTokenGenerator()
