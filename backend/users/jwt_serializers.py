from rest_framework import exceptions
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = "email"

    def validate(self, attrs):
        data = super().validate(attrs)
        # Block banned users from obtaining new tokens.
        if getattr(self.user, "is_banned", False):
            raise exceptions.AuthenticationFailed(
                "This account has been banned.", code="user_banned"
            )
        return data
