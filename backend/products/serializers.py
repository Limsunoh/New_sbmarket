from rest_framework import serializers

from backend.accounts.models import User
from backend.products.models import Hashtag, Image, Product


class AuthorSerializer(serializers.ModelSerializer):
    """
    작성자 정보 Serializer.
    - 닉네임과 프로필 이미지 URL 반환.
    """

    profile_image_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("nickname", "profile_image_url")

    def get_profile_image_url(self, obj):
        return obj.get_profile_image_url()


class HashtagSerializer(serializers.ModelSerializer):
    """
    해시태그 Serializer.
    - 해시태그 ID와 이름 반환.
    """

    class Meta:
        model = Hashtag
        fields = ("id", "name")


class ImageSerializer(serializers.ModelSerializer):
    """
    이미지 Serializer.
    - 이미지 ID와 URL 반환.
    """

    image_url = serializers.ImageField(use_url=True)

    class Meta:
        model = Image
        fields = ("id", "image_url")


class ProductListSerializer(serializers.ModelSerializer):
    """
    상품 목록 Serializer.
    - 주요 상품 정보와 첫 번째 이미지, 좋아요 수 반환.
    """

    preview_image = serializers.SerializerMethodField(read_only=True)
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

    def get_preview_image(self, instance):
        if instance.images.exists():
            return instance.images.order_by("id").first().image_url.url
        return None

    def get_likes_count(self, obj):
        return obj.likes.count()


class ProductCreateSerializer(serializers.ModelSerializer):
    """
    상품 생성 Serializer.
    - 상품 생성 시 태그와 이미지 처리.
    """

    class Meta:
        model = Product
        fields = ("title", "content", "price", "status", "tags", "images")

    def save_with_related_data(self, request):
        """
        태그와 이미지를 함께 저장.
        """
        tags = request.data.get("tags", "").split(",")
        images = request.FILES.getlist("images")
        product = self.save(author=request.user)

        # 태그 저장
        product.tags.clear()
        for tag in tags:
            hashtag, created = Hashtag.objects.get_or_create(name=tag.strip())
            product.tags.add(hashtag)

        # 이미지 저장
        for image in images:
            Image.objects.create(product=product, image_url=image)


class ProductDetailSerializer(serializers.ModelSerializer):
    """
    상품 상세 Serializer.
    - 상세 정보, 이미지, 태그, 좋아요 수 반환.
    """

    images = ImageSerializer(many=True, read_only=True)
    hashtag = HashtagSerializer(many=True, source="tags", required=False)
    likes_count = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "id",
            "images",
            "title",
            "content",
            "author",
            "price",
            "status",
            "hashtag",
            "hits",
            "created_at",
            "updated_at",
            "likes_count",
        )

    def get_likes_count(self, obj):
        return obj.likes.count()

    def save_with_related_data(self, request):
        """
        태그와 이미지를 업데이트.
        """
        instance = self.instance
        tags = request.data.get("tags", "").split(",")
        images = request.FILES.getlist("images")

        # 태그 업데이트
        instance.tags.clear()
        for tag in tags:
            hashtag, created = Hashtag.objects.get_or_create(name=tag.strip())
            instance.tags.add(hashtag)

        # 이미지 업데이트
        if images:
            instance.images.all().delete()
            for image in images:
                Image.objects.create(product=instance, image_url=image)

        return instance
