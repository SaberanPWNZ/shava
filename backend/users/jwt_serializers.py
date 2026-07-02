from rest_framework import exceptions
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = "email"

    def validate(self, attrs):
        data = super().validate(attrs)
        if getattr(self.user, "is_banned", False):
            raise exceptions.AuthenticationFailed(
                "This account has been banned.", code="user_banned"
            )
        return data
