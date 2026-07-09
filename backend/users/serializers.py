from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from rest_framework import serializers

from config.thumbnails import thumbnail_set
from places.models import City
from places.serializers import CityMinimalSerializer
from users.models import User, phone_validator
from users.serivces.services import RegistrationData, UserRegistrationService


def _avatar_thumbnails(serializer, obj):
    """Shared resolver for the ``avatar_thumbnails`` SerializerMethodField."""

    request = serializer.context.get("request")
    return thumbnail_set(
        getattr(obj, "avatar", None), alias_group="avatar", request=request
    )


class RegisterSerializer(serializers.ModelSerializer):
    """Public registration input. Whitelists fields explicitly.

    ``terms_accepted`` is write-only and required — it never lands on the
    model directly; instead it stamps ``terms_accepted_at`` at creation
    time, giving a durable record of *when* consent was given.
    """

    password = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
        validators=[validate_password],
    )
    email = serializers.EmailField(required=True)
    phone = serializers.CharField(
        required=False, allow_blank=True, validators=[phone_validator]
    )
    city = serializers.PrimaryKeyRelatedField(
        queryset=City.objects.filter(is_active=True), required=False, allow_null=True
    )
    terms_accepted = serializers.BooleanField(write_only=True, required=True)
    marketing_opt_in = serializers.BooleanField(required=False, default=False)

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "first_name",
            "last_name",
            "phone",
            "city",
            "terms_accepted",
            "marketing_opt_in",
        ]

    def validate_email(self, value: str) -> str:
        value = value.strip().lower()
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_terms_accepted(self, value: bool) -> bool:
        if not value:
            raise serializers.ValidationError(
                "You must accept the Terms of Service to register."
            )
        return value

    def create(self, validated_data):
        service: UserRegistrationService = (
            self.context.get("registration_service") or UserRegistrationService()
        )
        city = validated_data.get("city")
        return service.register(
            RegistrationData(
                email=validated_data["email"],
                password=validated_data["password"],
                first_name=validated_data.get("first_name") or "",
                last_name=validated_data.get("last_name") or "",
                phone=validated_data.get("phone") or "",
                city_id=city.pk if city else None,
                marketing_opt_in=bool(validated_data.get("marketing_opt_in")),
                terms_accepted_at=timezone.now(),
            )
        )


class UserPublicSerializer(serializers.ModelSerializer):
    """Safe, read-only view of a user — used for one's own profile
    (``/me/``) and by admins. Includes ``email``, so it must never be
    reused for a *different* user's profile (see
    :class:`UserPublicProfileSerializer` for that).
    """

    avatar_thumbnails = serializers.SerializerMethodField()
    city = CityMinimalSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "phone",
            "bio",
            "city",
            "avatar",
            "avatar_thumbnails",
            "is_verified",
            "marketing_opt_in",
        ]
        read_only_fields = fields

    def get_avatar_thumbnails(self, obj):
        return _avatar_thumbnails(self, obj)


class UserPublicProfileSerializer(serializers.ModelSerializer):
    """Safe view of *another* user's profile — no email, no phone.

    Suitable for surfacing on the leaderboard, review author links, etc.
    """

    avatar_thumbnails = serializers.SerializerMethodField()
    city = CityMinimalSerializer(read_only=True)
    member_since = serializers.DateTimeField(source="created_at", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "bio",
            "city",
            "avatar",
            "avatar_thumbnails",
            "member_since",
        ]
        read_only_fields = fields

    def get_avatar_thumbnails(self, obj):
        return _avatar_thumbnails(self, obj)


class MeUpdateSerializer(serializers.ModelSerializer):
    """Fields a user is allowed to change about themselves."""

    phone = serializers.CharField(
        required=False, allow_blank=True, validators=[phone_validator]
    )
    city = serializers.PrimaryKeyRelatedField(
        queryset=City.objects.filter(is_active=True), required=False, allow_null=True
    )

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "phone",
            "bio",
            "city",
            "avatar",
            "marketing_opt_in",
        ]


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


class AccountDeleteSerializer(serializers.Serializer):
    """Requires the current password so a hijacked, still-logged-in session
    (e.g. from a shared device) cannot self-delete the account silently."""

    password = serializers.CharField(write_only=True, required=True)

    def validate_password(self, value: str) -> str:
        user = self.context.get("user")
        if user is None or not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value


class UserAdminSerializer(serializers.ModelSerializer):
    """Full serializer; admin-only endpoints."""

    password = serializers.CharField(
        write_only=True,
        required=False,
        validators=[validate_password],
    )
    avatar_thumbnails = serializers.SerializerMethodField()
    city = serializers.PrimaryKeyRelatedField(
        queryset=City.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "phone",
            "bio",
            "city",
            "marketing_opt_in",
            "terms_accepted_at",
            "is_active",
            "is_staff",
            "is_superuser",
            "telegram_id",
            "avatar",
            "avatar_thumbnails",
            "is_verified",
            "is_banned",
            "is_moderator",
            "is_admin",
            "password",
        ]
        read_only_fields = ["id", "terms_accepted_at"]

    def get_avatar_thumbnails(self, obj):
        return _avatar_thumbnails(self, obj)

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
        validate_password(value)
        return value
