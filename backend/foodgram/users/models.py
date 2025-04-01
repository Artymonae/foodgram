"""Модуль с кастомной моделью пользователя."""
from django.contrib.auth import password_validation
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from users.constants import (
    MAX_EMAIL_LENGTH, MAX_NAME_LENGTH,
    MAX_PASSWORD_LENGTH, USERNAME_REGEX,)
from users.validators import blacklist_username, email_validator


class User(AbstractUser):
    """Кастомная модель пользователя с email в качестве логина."""

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = (
        "username",
        "first_name",
        "last_name",
        "password",
    )

    username = models.CharField(
        unique=True,
        verbose_name="Ник",
        max_length=MAX_NAME_LENGTH,
        validators=(RegexValidator(USERNAME_REGEX), blacklist_username),
    )
    email = models.EmailField(
        unique=True,
        verbose_name="Эл. Почта",
        max_length=MAX_EMAIL_LENGTH,
        validators=(email_validator,),
    )
    password = models.CharField(
        verbose_name="Пароль",
        max_length=MAX_PASSWORD_LENGTH,
    )
    first_name = models.CharField(
        verbose_name="Имя",
        max_length=MAX_NAME_LENGTH,
    )
    last_name = models.CharField(
        verbose_name="Фамилия",
        max_length=MAX_NAME_LENGTH,
    )
    avatar = models.ImageField(
        verbose_name="Аватарка",
        upload_to="users/avatars/",
        null=True,
        default=None,
    )
    groups = models.ManyToManyField(
        to="auth.Group",
        related_name="custom_user_groups",
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        to="auth.Permission",
        related_name="custom_user_permissions",
        blank=True,
    )

    class Meta:
        ordering = ("date_joined",)
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self._password is not None:
            password_validation.password_changed(self._password, self)
            self._password = None

        return self

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self._password = raw_password

        return self


class Follow(models.Model):
    """Модель подписки на пользователя."""

    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        verbose_name="Подписчик",
        related_name="following",
    )
    following = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        verbose_name="На кого подписан",
        related_name="followers",
    )

    class Meta:

        ordering = ("id",)
        verbose_name = "Подписчик"
        verbose_name_plural = "Подписчики"
        constraints = [
            models.UniqueConstraint(
                fields=(
                    "user",
                    "following",
                ),
                name="unique_subscription",
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F("following")),
                name="self_sub_prohibited",
            ),
        ]

    def __str__(self):
        return f"Подписка {self.user} на {self.following}"
