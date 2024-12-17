from django.contrib import admin
from django.urls import path, include
from django.templatetags.static import static
from django.conf import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/accounts/", include("backend.accounts.urls")),
    path("api/products/", include("backend.products.urls")),
    path("api/reviews/", include("backend.reviews.urls")),
    path("api/manager/", include("backend.manager.urls")),
    path("accounts/", include("frontend.accounts.urls")),
    path("products/", include("frontend.products.urls")),
    path("reviews/", include("frontend.reviews.urls")),
]
