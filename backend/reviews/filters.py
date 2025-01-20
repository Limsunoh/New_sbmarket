import django_filters

from .models import Review


class ReviewFilter(django_filters.FilterSet):
    """
    리뷰 필터링 클래스.
    - 특정 유저가 작성한 리뷰 또는 특정 상품에 대한 리뷰를 필터링.
    """

    author = django_filters.NumberFilter(field_name="author__id", lookup_expr="exact")
    product = django_filters.NumberFilter(field_name="product__id", lookup_expr="exact")
    is_deleted = django_filters.BooleanFilter(field_name="is_deleted", lookup_expr="exact")

    class Meta:
        model = Review
        fields = ["author", "product", "is_deleted"]
