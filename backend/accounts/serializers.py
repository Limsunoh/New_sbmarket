from django.core.validators import RegexValidator
from django.db import models
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from backend.accounts.models import User
from backend.products.models import Product
from backend.products.serializers import ProductListSerializer

# Custom RegexValidator for password validation
password_regex_validator = RegexValidator(
    regex=r'^(?=.*[A-Za-z])(?=.*[\d])(?=.*[!@#$%^&*(),.?":{}|<>])(?!.*(.)\1\1).{10,}$',
    message="비밀번호는 최소 10자 이상이어야 하며, 숫자, 문자, 특수문자 중 2가지 이상을 포함해야 하고, 연속되는 동일 문자가 3회 이상 반복되지 않아야 합니다.",
)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    사용자 이름 포함 JWT 토큰 생성 및 이메일 인증 확인.
    """

    def validate(self, attrs):
        data = super().validate(attrs)

        # 이메일 인증 확인
        if not self.user.is_active:
            raise serializers.ValidationError(
                {"detail": "이메일 인증이 완료되지 않은 계정입니다."},
                code="not_verified",
            )

        # 사용자 이름 추가
        data["username"] = self.user.username

        # Refresh 및 Access 토큰 직접 생성
        refresh = RefreshToken.for_user(self.user)
        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)

        return data


class UserSerializer(serializers.ModelSerializer):
    """
    사용자 데이터를 직렬화 및 역직렬화하는 Serializer.

    - 회원가입 시 비밀번호 확인, 이메일 코드, 프로필 이미지 등을 처리합니다.
    - 사용자 생성 시 필요한 기본 유효성 검사를 포함합니다.
    """

    password = serializers.CharField(write_only=True, validators=[password_regex_validator], required=True)
    check_password = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=True, allow_blank=False)
    email_code = serializers.IntegerField(write_only=True, required=True)
    postcode = serializers.CharField(required=False)
    mainaddress = serializers.CharField(required=False)
    subaddress = serializers.CharField(required=False)
    profile_image = serializers.SerializerMethodField()
    total_score = serializers.FloatField(read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "password",
            "check_password",
            "name",
            "nickname",
            "birth",
            "email",
            "postcode",
            "mainaddress",
            "subaddress",
            "extraaddress",
            "image",
            "profile_image",
            "introduce",
            "created_at",
            "total_score",
        )
        read_only_fields = ("id", "created_at", "total_score")
        write_only_fields = ("password", "check_password", "email_code", "image")

    def validate(self, data):
        """
        데이터 검증.

        - 비밀번호와 확인 비밀번호가 일치하는지 확인합니다.
        - 유효하지 않으면 ValidationError를 발생시킵니다.

        Args:
            data: 클라이언트에서 전달된 데이터.
        """
        if data["password"] != data["check_password"]:
            raise serializers.ValidationError({"check_password": "비밀번호가 일치하지 않습니다."})
        return data

    def create(self, validated_data):
        """
        사용자 생성.

        - 회원가입 데이터를 기반으로 새로운 사용자를 생성합니다.
        - 기본 프로필 이미지를 설정하고 초기 점수를 부여합니다.

        Args:
            validated_data: 검증된 데이터.
        """
        validated_data.pop("check_password", None)
        validated_data.pop("email_code", None)
        image = validated_data.get("image", None)
        if not image:
            image = "frontend/images/default_profile_image.jpg"

        user = User(
            username=validated_data["username"],
            email=validated_data["email"],
            name=validated_data.get("name", ""),
            nickname=validated_data.get("nickname", ""),
            birth=validated_data.get("birth", None),
            postcode=validated_data.get("postcode", ""),
            mainaddress=validated_data.get("mainaddress"),
            subaddress=validated_data.get("subaddress"),
            image=image,
            introduce=validated_data.get("introduce", ""),
        )
        user.set_password(validated_data["password"])
        user.is_active = False
        user.total_score = 30  # 기본 점수 설정
        user.save()

        return user


class ActivateUserSerializer(serializers.Serializer):
    """
    이메일 인증 데이터를 처리하는 Serializer.

    - 사용자 ID와 토큰을 검증하여 계정을 활성화합니다.
    """

    pk = serializers.CharField()
    token = serializers.CharField()

    def validate(self, data):
        """
        데이터 검증.

        - 사용자 ID를 디코딩하고, 유효한 토큰인지 확인합니다.
        - 계정이 존재하지 않거나 토큰이 잘못된 경우 ValidationError를 발생시킵니다.

        Args:
            data: 클라이언트에서 전달된 데이터.
        """
        try:
            # 사용자 ID 복원
            user_id = force_str(urlsafe_base64_decode(data["pk"]))
            user = User.objects.get(pk=user_id)

            # 토큰 유효성 확인
            token_obj = AccessToken(data["token"])
            if token_obj["user_id"] != user.id:
                raise serializers.ValidationError("유효하지 않은 토큰입니다.")

            # 검증 성공 시 user 객체 추가
            data["user"] = user
            return data
        except User.DoesNotExist:
            raise serializers.ValidationError("사용자가 존재하지 않습니다.")
        except Exception as e:
            raise serializers.ValidationError(f"에러 발생: {str(e)}")


class UserFollowSerializer(serializers.ModelSerializer):
    """
    사용자 팔로우 직렬화.
    """

    class Meta:
        model = User
        fields = ("id", "username", "nickname", "image")

    def toggle_follow(self, current_user, target_user):
        """
        팔로우 상태를 반전시키는 메서드.

        Args:
            current_user: 현재 요청을 보낸 사용자.
            target_user: 팔로우 대상 사용자.
        """
        if current_user in target_user.followers.all():
            target_user.followers.remove(current_user)
            return {"message": "unfollow했습니다."}

        target_user.followers.add(current_user)
        return {"message": "follow했습니다."}

    def is_following(self, current_user, target_user):
        """
        특정 사용자를 팔로우 중인지 확인.

        Args:
            current_user: 현재 요청을 보낸 사용자.
            target_user: 팔로우 대상 사용자.
        """
        return current_user in target_user.followers.all()


class UserProfileSerializer(serializers.ModelSerializer):
    """
    사용자 프로필 정보를 직렬화하는 Serializer.

    - 작성한 상품, 찜한 상품, 팔로잉, 팔로워, 리뷰 데이터를 포함.
    - 프로필 이미지와 생성일을 포맷팅하여 제공.
    """

    products = serializers.SerializerMethodField()
    like_products = serializers.SerializerMethodField()
    followings = serializers.SerializerMethodField()
    followers = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()
    profile_image = serializers.SerializerMethodField()
    total_score = serializers.FloatField(read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d", read_only=True)

    class Meta:
        model = User
        fields = (
            "name",
            "nickname",
            "birth",
            "email",
            "postcode",
            "mainaddress",
            "subaddress",
            "extraaddress",
            "created_at",
            "image",
            "profile_image",
            "introduce",
            "products",
            "like_products",
            "followings",
            "followers",
            "reviews",
            "total_score",
        )

    def get_profile_image(self, obj):
        """프로필 이미지 URL을 반환합니다."""
        return obj.get_profile_image_url()

    def get_products(self, obj):
        """유저가 작성한 상품 목록을 반환합니다."""
        products = Product.objects.filter(author=obj)
        return ProductListSerializer(products, many=True).data

    def get_like_products(self, obj):
        """유저가 찜한 상품 목록을 반환합니다."""
        like_products = obj.like_products.all()
        return ProductListSerializer(like_products, many=True).data

    def get_followings(self, obj):
        """유저가 팔로잉한 사용자 목록을 반환합니다."""
        followings = obj.followings.all()
        return UserFollowSerializer(followings, many=True).data

    def get_followers(self, obj):
        """유저를 팔로우하는 사용자 목록을 반환합니다."""
        followers = obj.followers.all()
        return UserFollowSerializer(followers, many=True).data

    # def get_reviews(self, obj):
    #     """유저가 작성한 리뷰 목록을 반환합니다."""
    #     reviews = Review.objects.filter(author=obj)
    #     return ReviewSerializer(reviews, many=True).data

    def get_review_score_total(self, obj):
        """
        유저가 작성한 제품에 대한 리뷰 점수 총합을 계산합니다.
        """
        total_score = 0
        products = Product.objects.filter(author=obj)

        # 각 제품의 리뷰 점수를 합산
        for product in products:
            total_score += product.reviews.aggregate(models.Sum("score"))["score__sum"] or 0

        return total_score


class UserChangeSerializer(serializers.ModelSerializer):
    """
    사용자 정보를 수정하는 Serializer.
    """

    profile_image = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "username",
            "nickname",
            "name",
            "postcode",
            "mainaddress",
            "subaddress",
            "extraaddress",
            "birth",
            "email",
            "image",
            "profile_image",
            "introduce",
        )
        read_only_fields = ("username",)

    def get_profile_image(self, obj):
        """
        프로필 이미지 URL 반환.
        """
        return obj.get_profile_image_url()

    def update(self, instance, validated_data):
        """
        사용자 프로필 업데이트 로직.
        """
        remove_image = self.context["request"].data.get("remove_image")
        new_image = self.context["request"].FILES.get("image")

        # 프로필 이미지 처리
        instance.handle_profile_image(remove_image, new_image)

        # 나머지 필드 업데이트
        for field, value in validated_data.items():
            setattr(instance, field, value)

        instance.save()
        return instance


class ChangePasswordSerializer(serializers.Serializer):
    """
    사용자 비밀번호 변경을 위한 Serializer.

    - 입력 필드:
        - current_password: 현재 비밀번호
        - new_password: 새 비밀번호
        - password_check: 새 비밀번호 확인
    """

    current_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True, validators=[password_regex_validator])
    password_check = serializers.CharField(write_only=True, required=True)

    def validate_current_password(self, value):
        """
        현재 비밀번호 검증.

        - 현재 비밀번호가 올바르지 않으면 ValidationError를 발생시킵니다.
        """
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("현재 비밀번호가 올바르지 않습니다.")
        return value

    def validate(self, data):
        """
        데이터 검증.

        - 새 비밀번호와 비밀번호 확인이 일치하는지 확인합니다.
        """
        new_password = data.get("new_password")
        password_check = data.get("password_check")

        if new_password != password_check:
            raise serializers.ValidationError({"password_check": "새 비밀번호가 일치하지 않습니다."})

        return data

    def update(self, instance, validated_data):
        """
        사용자 비밀번호 업데이트.

        - 새 비밀번호를 설정하고 저장합니다.
        """
        instance.set_password(validated_data["new_password"])
        instance.save()
        return instance


class UserListSerializer(serializers.ModelSerializer):
    profile_image = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "nickname",
            "profile_image",
        )

    def get_profile_image(self, obj):
        return obj.get_profile_image_url()
