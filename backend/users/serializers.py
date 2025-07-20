from rest_framework import serializers
from users.models import User
from django.contrib.auth.password_validation import validate_password


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
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
        read_only_fields = [
            "id",
            "is_active",
            "is_staff",
            "is_superuser",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        email = validated_data.get("email")
        password = validated_data.pop("password")

        # Ensure username is set to email if not provided
        if not validated_data.get("username"):
            validated_data["username"] = email

        user = User.objects.create_user(
            email=email, password=password, **validated_data
        )
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance
