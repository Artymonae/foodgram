from django.contrib import admin
from recipes.models import (
    Tag, Ingredient, Recipe,
    RecipeIngredient, Favorite,
    ShoppingCart,
)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "slug",
    )
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "measurement_unit",
    )
    search_fields = ("name",)
    ordering = ("name",)


class RecipeIngredientInline(admin.TabularInline):

    model = RecipeIngredient
    extra = 1
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "author",
        "pub_date",
        "cooking_time",
    )
    list_filter = (
        "pub_date",
        "tags",
        "author",
    )
    search_fields = (
        "name",
        "text",
        "author__username",
    )
    inlines = [RecipeIngredientInline]
    ordering = ("-pub_date",)
    readonly_fields = ("pub_date",)


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):

    list_display = (
        "recipe",
        "ingredient",
        "amount",
    )
    list_filter = (
        "recipe",
        "ingredient",
    )
    search_fields = (
        "recipe__name",
        "ingredient__name",
    )


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "recipe",
        "pub_date",
    )
    list_filter = (
        "user",
        "recipe",
    )
    search_fields = (
        "user__username",
        "recipe__name",
    )
    ordering = ("-pub_date",)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "recipe",
        "pub_date",
    )
    list_filter = (
        "user",
        "recipe",
    )
    search_fields = (
        "user__username",
        "recipe__name",
    )
    ordering = ("-pub_date",)
