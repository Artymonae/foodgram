"""Модуль для миксинов и вспомогательных утилит."""
import uuid
import random
import logging

from recipes.constants import LENGTH_SHORT_LINK


logger = logging.getLogger(__name__)


class ShortLink:
    """ Создание короткой уникальной ссылки."""
    @staticmethod
    def create_short_link(length=LENGTH_SHORT_LINK):
        """Создает короткую ссылку."""
        u1 = uuid.uuid5(uuid.NAMESPACE_DNS, uuid.uuid4().hex)
        u2 = uuid.uuid5(uuid.NAMESPACE_DNS, uuid.uuid4().hex)

        combined = u1.hex + u2.hex

        chars = list(combined)
        random.shuffle(chars)

        return "".join(chars)[:length]
