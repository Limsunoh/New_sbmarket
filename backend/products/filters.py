from django.db.models import Count, Q
from django_filters import rest_framework as filters

from .models import Product


class ProductFilter(filters.FilterSet):
    search = filters.CharFilter(method="filter_search")  # 사용자 정의 메서드
    hashtag = filters.CharFilter(field_name="tags__name", lookup_expr="iexact")
    order_by = filters.OrderingFilter(
        fields=["likes_count", "hits", "created_at"],  # 정렬 필드 정의
        field_labels={
            "likes_count": "좋아요",
            "hits": "조회수",
            "created_at": "최신순",
        },
    )

    class Meta:
        model = Product
        fields = ["hashtag", "search"]

    def filter_search(self, queryset, name, value):
        return queryset.filter(Q(title__icontains=value) | Q(content__icontains=value) | Q(tags__name__icontains=value)).distinct()

    def filter_order_by(self, queryset, name, value):
        if value == "likes":
            return queryset.annotate(likes_count=Count("likes")).order_by("-likes_count")
        if value == "hits":
            return queryset.order_by("-hits")
        return queryset.order_by("-created_at")
