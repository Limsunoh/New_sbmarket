from django.urls import path

from . import views

urlpatterns = [
    path("", views.ProductListAPIView.as_view(), name="product_list"),
    path("<int:pk>/", views.ProductDetailAPIView.as_view(), name="product_detail"),
    path("<int:pk>/like/", views.LikeAPIView.as_view(), name="like"),
    # path("aisearch/", views.AISearchAPIView.as_view(), name="ai_search"),
]
