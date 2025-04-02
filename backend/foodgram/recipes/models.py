"""Модуль с моделями для приложения."""
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from recipes.constants import (
    MAX_LENGTH_TITLE_RECIPE, MAX_VIEW_LENGTH,
    MIN_COOKING_TIME, MIN_SUM_INGREDIENT,
    MAX_LINK_LENGTH, MAX_LENGTH_OF_TAGS,
    MAX_LENGTH_OF_RECIPE_NAME, MAX_LENGTH_OF_RECIPE_UNIT,
)

User = get_user_model()


class Tag(models.Model):
    """Тег рецепта."""

    name = models.CharField(
        unique=True,
        verbose_name="Имя тега",
        max_length=MAX_LENGTH_OF_TAGS,
    )
    slug = models.SlugField(
        unique=True,
        verbose_name="Слаг",
        max_length=MAX_LENGTH_OF_TAGS,
    )

    class Meta:

        ordering = ("name",)
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name[:MAX_VIEW_LENGTH]


class Ingredient(models.Model):
    """Ингредиент рецепта."""

    name = models.CharField(
        verbose_name="Название ингридиента",
        max_length=MAX_LENGTH_OF_RECIPE_NAME,
    )
    measurement_unit = models.CharField(
        verbose_name="Единица измерения",
        max_length=MAX_LENGTH_OF_RECIPE_UNIT,
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        constraints = [
            models.UniqueConstraint(
                fields=("name", "measurement_unit",),
                name="unique_ingredient_unit",
            ),
        ]

    def __str__(self):
        return self.name[:MAX_VIEW_LENGTH]


class Recipe(models.Model):
    """Рецепт блюда."""

    author = models.ForeignKey(
        to=User,
        verbose_name="Автор",
        related_name="recipes",
        on_delete=models.CASCADE,
    )
    name = models.CharField(
        verbose_name="Название",
        max_length=MAX_LENGTH_TITLE_RECIPE,
    )
    text = models.TextField(
        verbose_name="Описание",
    )
    image = models.ImageField(
        verbose_name="Картинка блюда",
        upload_to="images",
    )
    cooking_time = models.PositiveIntegerField(
        validators=(MinValueValidator(MIN_COOKING_TIME),),
        verbose_name="Время готовки",
    )
    pub_date = models.DateTimeField(
        verbose_name="Дата добавления",
        default=timezone.now,
        db_index=True,
    )
    ingredients = models.ManyToManyField(
        to=Ingredient,
        verbose_name="Ингредиенты",
        through="RecipeIngredient",
    )
    tags = models.ManyToManyField(
        to=Tag,
        verbose_name="Тэги",
    )
    short_link = models.CharField(
        verbose_name="Короткая ссылка",
        max_length=MAX_LINK_LENGTH,
        unique=True,
        blank=True,
        null=True,
    )

    class Meta:

        default_related_name = "recipes"
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ("pub_date",)

    def __str__(self):
        return self.name[:MAX_VIEW_LENGTH]


class RecipeIngredient(models.Model):
    """Ингредиент в рецепте."""

    recipe = models.ForeignKey(
        to=Recipe,
        verbose_name="Рецепт",
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        to=Ingredient,
        verbose_name="Ингредиент",
        on_delete=models.CASCADE,
    )
    amount = models.PositiveIntegerField(
        verbose_name="Количество объем",
        validators=[
            MinValueValidator(MIN_SUM_INGREDIENT),
        ],
    )

    class Meta:

        verbose_name = "Ингредиент Рецепта"
        verbose_name_plural = "Ингредиенты Рецептов"
        default_related_name = "recipe_ingredients"
        constraints = [
            models.UniqueConstraint(
                fields=(
                    "ingredient",
                    "recipe",
                ),
                name="unique_recipe_ingredient",
            )
        ]

    def __str__(self):
        return f"{self.recipe.name[:MAX_VIEW_LENGTH]} - {self.ingredient}"


class BaseFavoriteShoppingCart(models.Model):
    """ База для избранного и корзины."""

    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        verbose_name="Автор",
    )
    recipe = models.ForeignKey(
        to=Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
    )
    pub_date = models.DateTimeField(
        verbose_name="Дата добавления",
        default=timezone.now,
        db_index=True,
    )

    class Meta:

        abstract = True
        ordering = ("-pub_date",)


class Favorite(BaseFavoriteShoppingCart):
    """Избранные рецепты."""

    class Meta(BaseFavoriteShoppingCart.Meta):

        abstract = False
        default_related_name = "favorites"
        verbose_name = "Избранное"
        verbose_name_plural = "Избранные"
        constraints = [
            models.UniqueConstraint(
                fields=(
                    "user",
                    "recipe",
                ),
                name="unique_user_favorite_recipe",
            )
        ]

    def __str__(self):
        return f"Избранное: {self.recipe} у {self.user}"


class ShoppingCart(BaseFavoriteShoppingCart):
    """Корзина покупок."""

    class Meta(BaseFavoriteShoppingCart.Meta):

        abstract = False
        default_related_name = "shoppingcarts"
        verbose_name = "Корзина"
        verbose_name_plural = "Корзина"
        constraints = [
            models.UniqueConstraint(
                fields=(
                    "user",
                    "recipe",
                ),
                name="unique_user_shoppingcart_recipe",
            )
        ]

    def __str__(self):
        return f"{self.recipe} в корзине {self.user}"
