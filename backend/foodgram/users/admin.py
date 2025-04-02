from django.contrib import admin
from django.db.models import Count
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _

from users.forms import UserAdminCreationForm, UserAdminForm
from users.models import Follow

User = get_user_model()


@admin.register(User)
class UserAdmin(DjangoUserAdmin):

    form = UserAdminForm
    add_form = UserAdminCreationForm
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_active",
        "role",
        "recipe_count",
        "follower_count",
        "last_login",
    )
    list_filter = (
        "groups",
        "is_active",
    )
    search_fields = (
        "email",
        "username",
        "first_name",
        "last_name",
    )
    readonly_fields = (
        "date_joined",
        "last_login",
        "role",
    )
    fieldsets = (
        (
            None, {
                "fields":
                (
                    "username",
                    "email",
                    "password",
                )
            }
        ),
        (
            _("Personal Info"), {
                "fields":
                (
                    "first_name",
                    "last_name",
                    "avatar",
                )
            }
        ),
        (
            _("Permissions"), {
                "fields":
                (
                    "is_active",
                    "groups",
                    "user_permissions",
                )
            }
        ),
        (
            _("Important Dates"), {
                "fields":
                (
                    "last_login",
                    "date_joined",
                )
            }
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": (
                    "wide",
                ),
                "fields": (
                    "username",
                    "email",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                ),
            },
        ),
    )

    @admin.display(description="Роль")
    def role(self, obj):
        return obj.groups.first()

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            recipe_count=Count("recipes", distinct=True),
            follower_count=Count("followers", distinct=True)
        ).prefetch_related("groups")
        return queryset

    @admin.display(description="Рецепты")
    def recipe_count(self, obj):
        return obj.recipe_count

    @admin.display(description="Подписчики")
    def follower_count(self, obj):
        return obj.follower_count


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):

    list_display = ("user", "following",)
    list_filter = ("user", "following",)
    search_fields = (
        "user__username",
        "user__email",
        "following__username",
        "following__email",
    )
    autocomplete_fields = ("user", "following",)
