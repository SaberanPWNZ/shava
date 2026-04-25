"""Serializers for the users app.

The serializers are intentionally split by responsibility (SRP/ISP):

* :class:`RegisterSerializer` — public registration input. Accepts only fields
  the client may legitimately set; privileged flags can never be assigned via
  this serializer.
* :class:`UserPublicSerializer` — read-only representation safe to expose to
  any authenticated user (their own profile or a public listing).
* :class:`MeUpdateSerializer` — the limited subset a user can change about
  themselves.
* :class:`ChangePasswordSerializer` — old/new password with strong validation.
* :class:`UserAdminSerializer` — full set of fields, used **only** by
  admin-only endpoints.
"""

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from users.models import User
from users.services import RegistrationData, UserRegistrationService


class RegisterSerializer(serializers.ModelSerializer):
    """Public registration input. Whitelists fields explicitly."""

    password = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
        validators=[validate_password],
    )
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ["email", "password", "first_name", "last_name"]

    def validate_email(self, value: str) -> str:
        value = value.strip().lower()
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        service: UserRegistrationService = (
            self.context.get("registration_service") or UserRegistrationService()
        )
        return service.register(
            RegistrationData(
                email=validated_data["email"],
                password=validated_data["password"],
                first_name=validated_data.get("first_name") or "",
                last_name=validated_data.get("last_name") or "",
            )
        )


class UserPublicSerializer(serializers.ModelSerializer):
    """Safe, read-only view of a user."""

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "avatar",
            "is_verified",
        ]
        read_only_fields = fields


class MeUpdateSerializer(serializers.ModelSerializer):
    """Fields a user is allowed to change about themselves."""

    class Meta:
        model = User
        fields = ["first_name", "last_name", "avatar"]


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True)

    def validate_new_password(self, value: str) -> str:
        validate_password(value, user=self.context.get("user"))
        return value

    def validate(self, attrs):
        user = self.context.get("user")
        if user is None or not user.check_password(attrs["old_password"]):
            raise serializers.ValidationError(
                {"old_password": "Current password is incorrect."}
            )
        if attrs["old_password"] == attrs["new_password"]:
            raise serializers.ValidationError(
                {"new_password": "New password must differ from the old one."}
            )
        return attrs


class UserAdminSerializer(serializers.ModelSerializer):
    """Full serializer; admin-only endpoints."""

    password = serializers.CharField(
        write_only=True,
        required=False,
        validators=[validate_password],
    )

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_active",
            "is_staff",
            "is_superuser",
            "telegram_id",
            "avatar",
            "is_verified",
            "is_banned",
            "is_moderator",
            "is_admin",
            "password",
        ]
        read_only_fields = ["id"]

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class VerifyEmailConfirmSerializer(serializers.Serializer):
    """Public — accepts a signed token and marks the user as verified."""

    token = serializers.CharField(required=True, write_only=True)


class PasswordResetRequestSerializer(serializers.Serializer):
    """Public — requests a password-reset link by email.

    Validation here is *deliberately* lenient: the view never reveals
    whether the address is registered, so we only check the format.
    """

    email = serializers.EmailField(required=True)

    def validate_email(self, value: str) -> str:
        return value.strip().lower()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Public — completes a password reset using a signed token."""

    token = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)

    def validate_new_password(self, value: str) -> str:
        # The user is resolved from the token in the view, so we can only
        # apply password validators that don't need a user instance here.
        # The view runs ``validate_password(value, user=user)`` again with
        # the resolved user for similarity checks.
        validate_password(value)
        return value
