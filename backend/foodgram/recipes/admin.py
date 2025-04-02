from django.contrib import admin
from django.db.models import Count
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
        "favorites_count",
        "display_ingredients",
        "display_tags",
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

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.prefetch_related('ingredients', 'tags')
        queryset = queryset.annotate(favorites_count=Count('favorites'))
        return queryset

    @admin.display(description="В избранном")
    def favorites_count(self, obj):
        return obj.favorites_count

    @admin.display(description="Ингредиенты")
    def display_ingredients(self, obj):
        return ", ".join(
            [ingredient.name for ingredient in obj.ingredients.all()]
        )

    @admin.display(description="Теги")
    def display_tags(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()])


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
