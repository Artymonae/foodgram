"""Модуль для миксинов и вспомогательных утилит."""
import base64
import uuid
import random
import logging

from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import pagination, serializers, status

from recipes.constants import PAGE_SIZE
from recipes.models import Recipe


logger = logging.getLogger(__name__)


class Base64ImageField(serializers.ImageField):
    """Превращаем картинку из запроса в картинку-файл."""

    def to_internal_value(self, data):
        """Преобразует строку base64 в ImageField."""
        if isinstance(data, str) and data.startswith("data:image"):
            file_format, image = data.split(";base64,")
            file_extension = file_format.split("/")[1]
            data = ContentFile(
                base64.b64decode(image),
                name=f"{uuid.uuid4()}.{file_extension}",
            )
        return super().to_internal_value(data)


class ShortLink:
    """ Создание короткой уникальной ссылки."""
    @staticmethod
    def create_short_link(length=12):
        """Создает короткую ссылку."""
        u1 = uuid.uuid5(uuid.NAMESPACE_DNS, uuid.uuid4().hex)
        u2 = uuid.uuid5(uuid.NAMESPACE_DNS, uuid.uuid4().hex)

        combined = u1.hex + u2.hex

        chars = list(combined)
        random.shuffle(chars)

        return "".join(chars)[:length]


class Pagination(pagination.PageNumberPagination):
    """Пагинации."""

    page_size = PAGE_SIZE
    max_page_size = PAGE_SIZE
    page_size_query_param = "limit"


class RecipeActionMixin:
    """Миксин для добавления/удаления рецептов из избранного и корзины."""

    def modify_recipe_in_list(
        self,
        request,
        pk,
        serializer_class,
        model_class
    ):
        recipe = get_object_or_404(Recipe, id=pk)

        logger.info(
            "User %s requested %s for recipe %s",
            request.user,
            request.method,
            recipe,
        )
        if request.method == "POST":
            data = {
                "recipe": recipe.id,
                "user": request.user.id,
                "context": {"request": request},
            }
            serializer = serializer_class(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            logger.info(
                "Recipe %s added to %s for user %s",
                recipe,
                model_class.__name__,
                request.user,
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == "DELETE":
            instance = model_class.objects.filter(
                user=request.user, recipe=recipe,
            )
            if not instance.exists():
                logger.error(
                    "Recipe %s not found in %s for user %s",
                    recipe,
                    model_class.__name__,
                    request.user,
                )
                return Response(
                    {"error": "Рецепт не найден"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            instance.delete()

            logger.info(
                "Recipe %s removed from %s for user %s",
                recipe,
                model_class.__name__,
                request.user,
            )
            return Response(status=status.HTTP_204_NO_CONTENT)
