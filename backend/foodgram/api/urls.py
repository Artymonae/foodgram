from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api import views


app_name = "api"

router = DefaultRouter()

router.register("recipes", views.RecipesViewSet, basename="recipes")
router.register("users", views.UserViewSet, basename="users")
router.register("tags", views.TagViewSet, basename="tags")
router.register("ingredients", views.IngredientViewSet, basename="ingredients")

api_patterns = [
    path("", include(router.urls)),
    path("auth/", include("djoser.urls.authtoken")),
]

urlpatterns = [
    path("", include((api_patterns, app_name))),
]
