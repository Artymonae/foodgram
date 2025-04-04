"""Модуль сериализаторов для API-сервиса."""
import logging

from djoser.serializers import UserSerializer as DjoserUser
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator


from api.fields import Base64ImageField
from recipes.models import (
    Favorite, Ingredient, Recipe,
    RecipeIngredient, ShoppingCart, Tag,)
from users.models import Follow, User


logger = logging.getLogger(__name__)


class UserSerializer(DjoserUser):
    """Сериализатор пользователя для получения данных с инф. о подписке."""

    is_subscribed = serializers.SerializerMethodField(
        method_name="get_is_followed",
    )
    avatar = Base64ImageField()

    class Meta(DjoserUser.Meta):

        fields = DjoserUser.Meta.fields + (
            "is_subscribed",
            "avatar",
        )

    def get_is_followed(self, obj):
        request = self.context.get("request")
        return (
            request
            and request.user.is_authenticated
            and request.user.following.filter(following=obj).exists()
        )


class UserAvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления аватара пользователя."""

    avatar = Base64ImageField()

    class Meta:

        model = User
        fields = ("avatar",)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов."""

    class Meta:

        model = Tag
        fields = "__all__"


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    class Meta:

        model = Ingredient
        fields = "__all__"


class CreateRecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для создания связи рецепт-ингредиент."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), source="ingredient",
    )

    class Meta:

        model = RecipeIngredient
        fields = ("id", "amount",)


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения ингредиентов рецепта."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), source="ingredient",
    )
    measurement_unit = serializers.CharField(
        source="ingredient.measurement_unit",
    )
    name = serializers.CharField(source="ingredient.name")

    class Meta:

        model = RecipeIngredient
        fields = ("id", "amount", "measurement_unit", "name",)


class GetRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для получения детальной информации о рецепте."""

    ingredients = RecipeIngredientSerializer(
        read_only=True,
        many=True,
        source="recipe_ingredients",
    )
    tags = TagSerializer(read_only=True, many=True)
    author = UserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField(
        method_name="get_is_in_favorite",
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name="get_is_in_shopping_cart",
    )

    class Meta:

        model = Recipe
        exclude = (
            "short_link",
            "pub_date",
        )

    def get_is_in_favorite(self, obj):
        request = self.context.get("request")
        return (
            request
            and request.user.is_authenticated
            and request.user.favorites.filter(recipe=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request")
        return (
            request
            and request.user.is_authenticated
            and request.user.shoppingcarts.filter(recipe=obj).exists()
        )


class RecipesSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления рецепта."""

    author = serializers.SlugRelatedField(
        slug_field="username",
        read_only=True,
    )
    image = Base64ImageField(required=True)
    ingredients = CreateRecipeIngredientSerializer(
        many=True, source="recipe_ingredients",
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )

    class Meta:

        model = Recipe
        fields = "__all__"

    def validate(self, attrs):
        tags = attrs.get("tags")
        ingredients = attrs.get("recipe_ingredients")
        if not tags:
            raise serializers.ValidationError(
                "Отсутствует обязательное поле tags",
            )
        if not ingredients:
            raise serializers.ValidationError(
                "Отсутствует обязательное поле ingredients",
            )

        ingredient_ids = [
            ingredient.get("ingredient").id
            for ingredient in ingredients
        ]

        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                "Ингредиенты должны быть уникальными.",
            )

        if len(tags) != len(set(tags)):
            raise serializers.ValidationError("Тэги должны быть уникальными.")

        return attrs

    def create(self, validated_data):
        recipe, _ = self._add_or_update_recipe_relations(validated_data)
        logger.info(
            "Created new recipe: %s by user %s",
            recipe,
            self.context.get("request").user,
        )
        return recipe

    def update(self, instance, validated_data):
        recipe, remaining_data = self._add_or_update_recipe_relations(
            validated_data, recipe=instance,
        )

        logger.info("Recipe was updated: %s", recipe)
        return super().update(recipe, remaining_data)

    def to_representation(self, instance):
        return GetRecipeSerializer(
            instance, context=self.context,
        ).data

    def _add_or_update_recipe_relations(self, validated_data, recipe=None):
        ingredients = validated_data.pop("recipe_ingredients")
        tags = validated_data.pop("tags")
        if recipe is None:
            recipe = Recipe.objects.create(**validated_data)
        else:
            recipe.recipe_ingredients.all().delete()
            recipe.tags.clear()

        recipe_ingredients = [
            RecipeIngredient(recipe=recipe, **ingredient)
            for ingredient in ingredients
        ]
        RecipeIngredient.objects.bulk_create(recipe_ingredients)
        recipe.tags.set(tags)
        return recipe, validated_data


class RecipeSerializer(serializers.ModelSerializer):
    """Короткий сериализатор рецепта для отображения в списках."""

    image = Base64ImageField(required=True)

    class Meta:

        model = Recipe
        fields = (
            "id",
            "name",
            "image",
            "cooking_time",
        )


class GetFollowSerializer(UserSerializer):
    """Сериализатор для получения информации о подписках пользователя."""

    recipes = serializers.SerializerMethodField(method_name="get_recipe")
    recipes_count = serializers.SerializerMethodField(
        method_name="get_recipes_count",
    )

    class Meta:
        model = User
        fields = UserSerializer.Meta.fields + (
            "recipes",
            "recipes_count",
        )

    def get_recipe(self, author):
        request = self.context.get("request")
        recipes = author.recipes.all()
        recipes_limit = request.GET.get("recipes_limit") if request else None

        if recipes_limit and recipes_limit.isdigit():
            recipes = recipes[:int(recipes_limit)]

        return RecipeSerializer(
            recipes, many=True, context=self.context
        ).data

    def get_recipes_count(self, user):
        return user.recipes.count()


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор для создания подписки."""

    ERROR_SELF_FOLLOW = "Попытка подписаться на самого себя."
    ERROR_ALREADY_FOLLOW = "Подписка уже существует."

    class Meta:

        model = Follow
        fields = ("user", "following",)

    def validate(self, attrs):
        follower, following = attrs["user"], attrs["following"]

        if follower == following:
            raise serializers.ValidationError(self.ERROR_SELF_FOLLOW)

        if Follow.objects.filter(user=follower, following=following).exists():
            raise serializers.ValidationError(self.ERROR_ALREADY_FOLLOW)

        return attrs

    def to_representation(self, instance):
        return GetFollowSerializer(
            instance.following, context=self.context,
        ).data


class UserRecipeRelationSerializerMixin(serializers.ModelSerializer):
    """Миксин для связей пользователь-рецепт."""

    class Meta:

        fields = ("user", "recipe",)

    def to_representation(self, instance):
        return RecipeSerializer(
            instance.recipe,
            context=self.context,
        ).data


class ShoppingCartSerializer(UserRecipeRelationSerializerMixin):
    """Сериализатор для корзины покупок."""

    class Meta(UserRecipeRelationSerializerMixin.Meta):

        model = ShoppingCart
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=("user", "recipe"),
            )
        ]


class FavoriteSerializer(UserRecipeRelationSerializerMixin):
    """Сериализатор для избранных рецептов."""

    class Meta(UserRecipeRelationSerializerMixin.Meta):

        model = Favorite
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=("user", "recipe"),
            ),
        ]
