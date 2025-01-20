from django.apps import apps
from rest_framework import serializers
from rest_framework.serializers import (
    CharField,
    DecimalField,
    ListField,
    ModelSerializer,
    SerializerMethodField,
)

from .models import Review

Product = apps.get_model("backend_products", "Product")


class ReviewSerializer(ModelSerializer):
    """
    리뷰 직렬화 클래스.
    """

    checklist = ListField(child=CharField(max_length=100))
    product_title = CharField(source="product.title", read_only=True)
    product_price = DecimalField(source="product.price", max_digits=10, decimal_places=2, read_only=True)
    product_image = SerializerMethodField()

    class Meta:
        model = Review
        fields = [
            "id",
            "author",
            "checklist",
            "additional_comments",
            "created_at",
            "score",
            "product_title",
            "product_price",
            "product_image",
            "product_id",
        ]
        read_only_fields = ["author", "created_at", "score"]

    def create(self, validated_data):
        """
        리뷰 생성 로직.
        """
        product = validated_data.get("product")
        author = self.context["request"].user
        checklist = validated_data.get("checklist")
        additional_comments = validated_data.get("additional_comments", "")

        try:
            return Review.create_review(
                author=author,
                product=product,
                checklist=checklist,
                additional_comments=additional_comments,
            )
        except ValueError as e:
            raise serializers.ValidationError({"detail": str(e)})

    def get_product_image(self, obj):
        """
        상품의 첫 번째 이미지를 반환.
        """
        image = obj.product.images.first()
        return image.image_url.url if image else "/static/images/default_image.jpg"


class PurchaseSerializer(ModelSerializer):
    """
    구매 상품 직렬화 클래스.
    """

    product_image = SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "price",
            "created_at",
            "product_image",
        ]

    def get_product_image(self, obj):
        """
        상품의 첫 번째 이미지를 반환.

        - 이미지가 없을 경우 기본 이미지를 반환합니다.
        """
        image = obj.images.first()
        return image.image_url.url if image else "/static/images/default_image.jpg"
