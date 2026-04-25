"""Custom DRF permissions for the users app.

These permissions are deliberately small and single-purpose (SRP/OCP) so that
new authorization rules can be added by composing or subclassing them rather
than by editing existing call sites.
"""

from rest_framework import permissions


class IsSelfOrAdmin(permissions.BasePermission):
    """Allow access if the request user is the object owner or a staff/admin."""

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_staff or user.is_superuser or getattr(user, "is_admin", False):
            return True
        return obj == user


class IsAdmin(permissions.BasePermission):
    """Allow access only to staff/superuser/admin users."""

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return bool(
            user.is_staff or user.is_superuser or getattr(user, "is_admin", False)
        )


class IsModerator(permissions.BasePermission):
    """Allow access to moderators (or higher: admin/staff)."""

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return bool(
            user.is_staff
            or user.is_superuser
            or getattr(user, "is_admin", False)
            or getattr(user, "is_moderator", False)
        )
