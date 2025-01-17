from rest_framework import serializers

from backend.accounts.models import User

from .models import Hashtag, Image, Product


# [작성자 정보 시리얼라이저] 작성자의 닉네임 + 프로필 이미지 URL 반환
class AuthorSerializer(serializers.ModelSerializer):
    profile_image_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("nickname", "profile_image_url")

    def get_profile_image_url(self, obj):
        return obj.get_profile_image_url()


# [해시태그 시리얼라이저] 해시태그 id, 이름 반환
class HashtagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hashtag
        fields = (
            "id",
            "name",
        )


# [이미지] 이미지 관련 정보 반환
class ImageSerializer(serializers.ModelSerializer):
    image_url = serializers.ImageField(use_url=True)

    class Meta:
        model = Image
        fields = (
            "id",
            "image_url",
        )


# [상품 목록] 상품의 주요 정보 반환
class ProductListSerializer(serializers.ModelSerializer):
    preview_image = serializers.SerializerMethodField(read_only=True)
    author = serializers.StringRelatedField(read_only=True)
    likes_count = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "id",
            "preview_image",
            "title",
            "author",
            "price",
            "status",
            "hits",
            "likes_count",
        )

    def get_likes_count(self, obj):
        # [좋아요 관련] 해당 상품의 좋아요 수를 반환
        return obj.likes.count()

    def get_preview_image(self, instance):
        # [미리보기 이미지] PK가 가장 낮은 이미지를 선택
        if instance.images.exists():
            lowest_pk_image = instance.images.order_by("id").first()
            return lowest_pk_image.image_url.url
        return None


# [상품 생성 시리얼라이저] 상품 생성 시 필요한 정보 반환
class ProductCreateSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField(read_only=True)
    hashtag = serializers.CharField(required=False)
    author = serializers.StringRelatedField()

    class Meta:
        model = Product
        fields = (
            "id",
            "title",
            "content",
            "author",
            "price",
            "status",
            "hashtag",
            "images",
        )
        write_only_fields = ("content",)

    def get_images(self, instance):
        # [이미지 URL 반환] 해당 상품의 이미지 url 목록
        if instance.images.exists():
            return list(instance.images.values_list("image_url", flat=True))
        return None


# [상품 상세 시리얼라이저] 상품의 상세 정보와 리뷰 정보 반환
class ProductDetailSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, read_only=True)
    hashtag = HashtagSerializer(many=True, source="tags", required=False)
    author = serializers.StringRelatedField()
    author_total_score = serializers.SerializerMethodField()
    author_profile_image_url = serializers.SerializerMethodField()
    mainaddress = serializers.CharField(source="author.mainaddress", read_only=True)
    likes_count = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "id",
            "images",
            "title",
            "content",
            "author",
            "author_total_score",
            "author_profile_image_url",
            "mainaddress",
            "price",
            "status",
            "hashtag",
            "hits",
            "created_at",
            "updated_at",
            "likes_count",
            "reviews",
        )

    def get_likes_count(self, obj):
        # [좋아요 수 반환] 상품의 좋아요 수 반환
        return obj.likes.count()

    def get_author_total_score(self, obj):
        # [작성자의 total_score를 반환]
        return obj.author.total_score

    def get_author_profile_image_url(self, obj):
        # [작성자 프로필 이미지 URL 반환] 작성자의 프로필 이미지 URL 반환
        return obj.author.get_profile_image_url()

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["status_display"] = instance.get_status_display()  # status의 디스플레이 값을 추가
        return rep
