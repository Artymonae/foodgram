"""Модуль вьюсетов для API-сервиса."""
import logging
from io import BytesIO

from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticated, IsAuthenticatedOrReadOnly,)
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilter
from api.helpers import ShortLink
from api.mixins import RecipeActionMixin
from api.paginations import Pagination
from api.permissions import OwnerOrReadOnly
from api.serializers import (
    CreateUserSerializer, FavoriteSerializer, FollowSerializer,
    GetFollowSerializer, IngredientSerializer, RecipesSerializer,
    ShoppingCartSerializer, TagSerializer, UserAvatarSerializer,
    UserSerializer,)
from recipes.constants import MAX_LINK_POSTFIX, URL
from recipes.models import (
    Favorite, Ingredient, Recipe,
    RecipeIngredient, ShoppingCart,
    Tag,)
from users.models import Follow

User = get_user_model()
logger = logging.getLogger(__name__)


class RecipesViewSet(RecipeActionMixin, viewsets.ModelViewSet):
    """Вьюсет для работы с рецептами."""

    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = Pagination
    permission_classes = (IsAuthenticatedOrReadOnly, OwnerOrReadOnly,)
    queryset = Recipe.objects.all()
    serializer_class = RecipesSerializer

    def perform_create(self, serializer):
        """Создает рецепт пользователем в БД."""
        serializer.save(author=self.request.user)
        logger.info("Recipe created by user %s", self.request.user)

    @staticmethod
    def _generate_unique_short_link():
        """Генерирует уникальный короткий идентификатор для рецепта."""
        short_link = ShortLink.create_short_link(MAX_LINK_POSTFIX)
        while Recipe.objects.filter(short_link=short_link).exists():
            short_link = ShortLink.create_short_link(MAX_LINK_POSTFIX)
        return short_link

    @action(
        methods=("GET",),
        detail=True,
        url_path="get-link",
    )
    def generate_short_link(self, request, pk):
        """Генерирует короткую ссылку."""
        recipe = get_object_or_404(Recipe, pk=pk)

        if recipe.short_link:
            logger.info("Short link to recipe %s exists", recipe)
            return Response(
                {"short-link": URL + recipe.short_link},
                status=status.HTTP_200_OK,
            )

        unique_short_link = self._generate_unique_short_link()
        recipe.short_link = unique_short_link
        recipe.save(update_fields=["short_link"])

        logger.info(
            "Short link %s created for recipe %s",
            unique_short_link,
            recipe,
        )
        return Response(
            {"short-link": URL + unique_short_link},
            status=status.HTTP_200_OK,
        )

    @action(
        methods=("POST", "DELETE",),
        detail=True,
        url_path="favorite",
        permission_classes=(IsAuthenticated,),
    )
    def add_to_favorite(self, request, pk):
        """Добавление рецепта в избранное."""
        return self.modify_recipe_in_list(
            request, pk, FavoriteSerializer, Favorite,
        )

    @action(
        methods=("POST", "DELETE",),
        detail=True,
        url_path="shopping_cart",
        permission_classes=(IsAuthenticated,),
    )
    def add_to_shopping_cart(self, request, pk):
        """Добавление рецепта в корзину."""
        return self.modify_recipe_in_list(
            request, pk, ShoppingCartSerializer, ShoppingCart,
        )

    @action(
        methods=("GET",),
        detail=False,
        url_path="download_shopping_cart",
        permission_classes=(IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        """Скачать корзину рецептов."""
        logger.info(
            "User %s requested to download shopping cart", request.user,
        )
        ingredients = (
            RecipeIngredient.objects.filter(
                recipe__shoppingcarts__user=request.user,
            )
            .values(
                "ingredient__name",
                "ingredient__measurement_unit",
            )
            .annotate(total_amount=Sum("amount"))
            .order_by("ingredient__name")
        )
        shopping_list = self.prepare_shopping_list(ingredients)
        return self.create_shopping_list_response(shopping_list)

    def prepare_shopping_list(self, ingredients):
        """Формирование списка покупок."""
        lines = [
            "%s (%s) — %s" % (
                item["ingredient__name"],
                item["ingredient__measurement_unit"],
                item["total_amount"]
            )
            for item in ingredients
        ]
        shopping_list = "\n".join(lines)

        logger.debug("Prepared shopping list: %s", shopping_list)
        return shopping_list

    def create_shopping_list_response(self, shopping_list):
        """Ответ с файлом списка покупок."""
        file_buffer = BytesIO(shopping_list.encode("utf-8"))
        response = FileResponse(file_buffer, content_type="text/plain")
        response["Content-Disposition"] = (
            "attachment; "
            "filename=\"shopping_list.txt\""
        )

        logger.info("Shopping list response created")
        return response


class UserViewSet(DjoserUserViewSet):
    """Вьюсет для работы с пользователями."""

    queryset = User.objects.all()
    serializer_class = CreateUserSerializer
    pagination_class = Pagination

    def get_serializer_class(self):
        """Получить класс сериализатора."""
        if self.action in ("list", "retrieve", "me",):
            return UserSerializer

        return super().get_serializer_class()

    @action(
        methods=("GET",),
        detail=False,
        url_path="me",
        permission_classes=(IsAuthenticated,),
    )
    def me(self, request):
        """Запрос пользователем профиля."""
        logger.info("User %s requested their profile", request.user)
        serializer = UserSerializer(request.user, context={"request": request})

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=("PUT", "DELETE",),
        detail=False,
        url_path="me/avatar",
        permission_classes=(IsAuthenticated,),
    )
    def user_avatar(self, request):
        """Изменение или удаление аватара."""
        user = get_object_or_404(User, username=request.user.username)
        if request.method == "PUT":
            serializer = UserAvatarSerializer(user, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            logger.info("User %s updated avatar", request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        request.user.avatar.delete()

        logger.info("User %s deleted avatar", request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=("POST", "DELETE",),
        detail=True,
        url_path="subscribe",
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, id):
        """Подписка/отписка на пользователя."""
        user = get_object_or_404(User, username=request.user.username)
        following = get_object_or_404(User, id=id)

        if request.method == "POST":
            serializer = FollowSerializer(
                data={"user": user.id, "following": following.id},
                context={"request": request},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

            logger.info("User %s subscribed to %s", user, following)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        follow = Follow.objects.filter(
            user=user.id, following=following.id,
        )
        if follow.exists():
            follow.delete()

            logger.info("User %s unsubscribed from %s", user, following)
            return Response(status=status.HTTP_204_NO_CONTENT)

        logger.error(
            "Subscription not found for user %s and following %s",
            user,
            following,
        )
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=("GET",),
        detail=False,
        url_path="subscriptions",
        permission_classes=(IsAuthenticated,),
    )
    def get_subscriptions(self, request):
        """Получение подписок."""
        user = get_object_or_404(User, username=request.user.username)
        following_users = User.objects.filter(following__user=user)

        result_page = self.paginate_queryset(following_users)
        serializer = GetFollowSerializer(
            result_page, many=True, context={"request": request},
        )

        logger.info("User %s requested subscriptions", request.user)
        return self.get_paginated_response(serializer.data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


def redirect_to_recipe_detail(request, short_link_code):
    """Редирект на детальную страницу рецепта."""
    recipe = get_object_or_404(Recipe, short_link=short_link_code)

    logger.info("Redirecting to recipe detail for recipe %s", recipe)
    return redirect("api:recipe-detail", pk=recipe.id)
