from django.contrib import admin
from django.conf import settings
from django.urls import include, path

from api.views import redirect_to_recipe_detail

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
    path(
        "s/<slug:short_link_code>/",
        redirect_to_recipe_detail,
        name="short_link_redirect",
    ),
]
if settings.DEBUG:
    import debug_toolbar
    # Добавить к списку urlpatterns список адресов из приложения debug_toolbar:
    urlpatterns += (path('__debug__/', include(debug_toolbar.urls)),)
