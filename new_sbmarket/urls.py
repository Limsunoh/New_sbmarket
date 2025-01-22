from django.contrib import admin
from django.urls import include, path

from frontend.products.views import HomePageView

urlpatterns = [
    path("", HomePageView.as_view(), name="home-page"),
    path("admin/", admin.site.urls),
    path("api/accounts/", include("backend.accounts.urls")),
    path("api/products/", include("backend.products.urls")),
    path("api/reviews/", include("backend.reviews.urls")),
    path("api/manager/", include("backend.manager.urls")),
    path("accounts/", include("frontend.accounts.urls")),
    path("products/", include("frontend.products.urls")),
    path("reviews/", include("frontend.reviews.urls")),
]
