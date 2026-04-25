"""Application services for the users app.

Keeps business logic out of serializers/views (SRP) and provides a clear
seam for testing and future extension (e.g. sending verification emails,
emitting domain events).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from users.models import User


@dataclass(frozen=True)
class RegistrationData:
    email: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserRegistrationService:
    """Creates regular users.

    The service is the *only* place that creates users from the public API,
    which guarantees that no privileged flag (``is_staff``, ``is_admin``,
    ``is_superuser``, ``is_moderator``, ``is_verified``) can ever be set via
    public input — preventing privilege-escalation regardless of what the
    serializer accepts.
    """

    def register(self, data: RegistrationData) -> User:
        return User.objects.create_user(
            email=data.email,
            password=data.password,
            first_name=data.first_name or "",
            last_name=data.last_name or "",
        )
