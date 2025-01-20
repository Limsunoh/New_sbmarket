from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from backend.products.models import Product
from backend.reviews.filters import ReviewFilter
from backend.reviews.models import Review
from backend.reviews.serializers import ReviewSerializer


class ReviewListCreateView(generics.ListCreateAPIView):
    """
    리뷰 목록 조회 및 생성 뷰.
    """

    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ReviewFilter

    def perform_create(self, serializer):
        """
        리뷰 생성 로직을 Serializer로 위임.
        """
        product_id = self.kwargs.get("product_id")
        product = get_object_or_404(Product, pk=product_id)
        serializer.save(product=product)


class ReviewDetailView(generics.RetrieveDestroyAPIView):
    """
    리뷰 상세 조회 및 삭제 뷰.

    - GET: 리뷰 상세 정보 반환.
    - DELETE: 리뷰 삭제 처리 (모델의 delete 메서드 호출).
    """

    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_destroy(self, instance):
        """
        리뷰 삭제 처리.
        - 모델의 delete 메서드를 호출하여 점수 유지 및 논리적 삭제 처리.
        """
        instance.delete()
