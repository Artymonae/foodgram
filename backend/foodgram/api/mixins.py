import logging

from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status

from recipes.models import Recipe


logger = logging.getLogger(__name__)


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
