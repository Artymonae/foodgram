"""Модуль для ограничений и разрешений пользователей."""
from rest_framework import permissions


class OwnerOrReadOnly(permissions.BasePermission):
    """"Создает разрешения для пользователя."""

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user == obj.author
        )
