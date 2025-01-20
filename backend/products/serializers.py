from rest_framework import serializers

from backend.accounts.models import User

from .models import Hashtag, Image, Product


# [작성자 정보 시리얼라이저] 작성자의 닉네임 + 프로필 이미지 URL 반환
class AuthorSerializer(serializers.ModelSerializer):
    profile_image_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "nickname",
            "profile_image_url",
        )

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
    class Meta:
        model = Product
        fields = ("title", "content", "price", "status", "tags", "images")

    def save_with_related_data(self, request):
        tags = request.data.get("tags", "").split(",")
        images = request.FILES.getlist("images")
        product = self.save(author=request.user)

        # Save tags
        product.tags.clear()
        for tag in tags:
            hashtag, created = Hashtag.objects.get_or_create(name=tag.strip())
            product.tags.add(hashtag)

        # Save images
        for image in images:
            Image.objects.create(product=product, image_url=image)


class ProductDetailSerializer(serializers.ModelSerializer):
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
        instance = self.instance
        tags = request.data.get("tags", "").split(",")
        images = request.FILES.getlist("images")

        # Update tags
        instance.tags.clear()
        for tag in tags:
            hashtag, created = Hashtag.objects.get_or_create(name=tag.strip())
            instance.tags.add(hashtag)

        # Update images
        if images:
            instance.images.all().delete()
            for image in images:
                Image.objects.create(product=instance, image_url=image)

        return instance
