"""Модуль с валидаторами приложения."""
import re

from django.core.exceptions import ValidationError

from users.constants import NOT_ALLOWED_USERNAME, MAX_LENGTH_VALIDATION_FIELD


def blacklist_username(value):
    """Запрещает никнеймы из черного списка."""
    if value in NOT_ALLOWED_USERNAME:
        raise ValidationError(f"{value} — данный никнейм запрещен.")
    return value


def email_validator(email):
    """Проверяет email на корректность и длину (до 150 символов)."""
    pattern = r"^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$"
    max_length = MAX_LENGTH_VALIDATION_FIELD

    if (
        len(email) > max_length
        or not re.fullmatch(pattern, email, re.IGNORECASE)
    ):
        raise ValidationError(
            "Некорректный email."
            "Допускаются латинские буквы, цифры и символы @/./+/-/_."
            f"Длина адреса не должна превышать {max_length} символов."
        )
