import json
import logging

import openai
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListCreateAPIView, UpdateAPIView
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from backend.products.filters import ProductFilter
from backend.products.models import Product
from backend.products.pagnations import ProductPagnation
from backend.products.serializers import (
    ProductCreateSerializer,
    ProductDetailSerializer,
    ProductListSerializer,
)
from new_sbmarket.config import OPENAI_API_KEY  # GPT 키는 config로 이전

logger = logging.getLogger(__name__)


class ProductListAPIView(ListCreateAPIView):
    """
    상품 목록 API.

    - GET: 상품 목록을 조회합니다.
    - POST: 새로운 상품을 생성합니다.
    """

    pagination_class = ProductPagnation
    serializer_class = ProductListSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filterset_class = ProductFilter

    def get_queryset(self):
        """상품 목록을 반환합니다."""
        return Product.objects.all()

    def post(self, request, *args, **kwargs):
        """새로운 상품을 생성합니다."""
        self.serializer_class = ProductCreateSerializer
        return super().post(request, *args, **kwargs)


class ProductDetailAPIView(UpdateAPIView):
    """
    상품 상세 API.

    - GET: 특정 상품의 상세 정보를 조회합니다.
    - PATCH/PUT: 상품 정보를 수정합니다.
    - DELETE: 상품을 삭제합니다.
    """

    queryset = Product.objects.all()
    serializer_class = ProductDetailSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, pk):
        """
        상품 상세 정보를 조회합니다.

        - 조회수 증가 처리를 포함합니다.
        """
        product = get_object_or_404(Product, pk=pk)
        user = self._authenticate_user(request)

        if user:
            viewed_products_key = f"viewed_products_{user.id}"
            product.increment_hits(user=user, viewed_products_key=viewed_products_key)
        else:
            product.increment_hits()

        return Response(ProductDetailSerializer(product).data)

    def _authenticate_user(self, request):
        """
        JWT 인증을 통해 사용자 객체를 반환합니다.
        """
        jwt_auth = JWTAuthentication()
        try:
            user_auth_data = jwt_auth.authenticate(request)
            return user_auth_data[0] if user_auth_data else None
        except Exception:
            return None

    def perform_update(self, serializer):
        """
        상품 정보를 저장하면서 관련 데이터를 처리합니다.
        """
        serializer.save_with_related_data(self.request)

    def delete(self, request, pk):
        """
        특정 상품을 삭제합니다.
        """
        product = get_object_or_404(Product, pk=pk)
        product.delete()
        return Response(status=204)


class LikeAPIView(APIView):
    """
    상품 찜 API.

    - GET: 특정 상품에 대한 찜 상태를 확인합니다.
    - POST: 찜하기 또는 찜하기 취소를 처리합니다.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        """
        특정 상품의 찜 상태를 확인합니다.
        """
        product = get_object_or_404(Product, pk=pk)
        is_liked = request.user in product.likes.all()
        return Response({"is_liked": is_liked}, status=200)

    def post(self, request, pk):
        """
        특정 상품에 대해 찜하기 또는 찜하기 취소를 처리합니다.
        """
        product = get_object_or_404(Product, pk=pk)
        if request.user in product.likes.all():
            product.likes.remove(request.user)
            return Response({"message": "찜하기 취소했습니다."}, status=200)
        product.likes.add(request.user)
        return Response({"message": "찜하기 했습니다."}, status=200)


class AISearchAPIView(APIView):
    """
    AI 검색 API.

    - 사용자의 요청에 따라 적합한 상품을 추천합니다.
    - OpenAI GPT를 사용하여 요청의 유해성을 검증하고, 핵심 키워드를 추출하며, 추천 목록을 생성합니다.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """
        AI를 사용하여 상품 검색 및 추천 처리.

        - 유해 요청 여부 확인
        - 핵심 키워드 추출
        - 추천 상품 생성
        """
        query = request.data.get("query", "")

        if not query:
            return Response({"error": "요구사항을 입력해주세요"}, status=400)

        openai.api_key = OPENAI_API_KEY

        # 유해 요청 여부 확인
        check_prompt = f"""
        요청이 서비스와 무관하거나 유해한 요청인지 확인해주세요.
        요청: "{query}"
        """
        check_response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": check_prompt}],
            temperature=0.2,
        )
        check_content = check_response.choices[0].message.content.strip()

        if "유해함" in check_content:
            return Response({}, status=204)

        # 핵심 키워드 추출
        keyword_prompt = f"""
        요청: '{query}'
        이 요청에서 핵심 키워드 1~2개를 추출하세요.
        """
        keyword_response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": keyword_prompt}],
            temperature=0.3,
        )
        keyword = keyword_response.choices[0].message.content.strip()

        # 상품 필터링
        filtered_products = Product.objects.filter(Q(title__icontains=keyword) | Q(tags__name__icontains=keyword)).distinct()

        if not filtered_products.exists():
            filtered_products = Product.objects.filter(status="sell").order_by("-created_at")[:50]

        product_list = [
            {
                "id": product.id,
                "title": product.title,
                "price": str(product.price),
                "preview_image": f"/media/{product.images.first().image_url}" if product.images.exists() else "/media/default-image.jpg",
                "author": product.author.username,
                "tags": [tag.name for tag in product.tags.all()],
                "likes_count": product.likes.count(),
                "hits": product.hits,
            }
            for product in filtered_products
        ]

        # 추천 요청
        recommend_prompt = f"""
        요청: '{query}'
        추천 상품:
        {product_list[:12]}
        """
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": recommend_prompt}],
            temperature=0.4,
        )
        raw_response = response.choices[0].message.content.strip()

        try:
            ai_response = json.loads(raw_response)
        except json.JSONDecodeError as e:
            logger.error(f"AI 응답 처리 중 오류 발생: {e}")
            return Response({"error": "AI 응답이 올바르지 않습니다."}, status=500)

        return Response({"response": ai_response}, status=200)
