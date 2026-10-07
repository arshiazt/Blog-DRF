from rest_framework_simplejwt.tokens import AccessToken
from datetime import timedelta

class PasswordResetToken(AccessToken):
    token_type = "password_reset"
    lifetime = timedelta(minutes=10)

    @classmethod
    def for_user(cls, user):
        token = cls()
        token["user_id"] = user.id
        token["token_type"] = cls.token_type

        return token