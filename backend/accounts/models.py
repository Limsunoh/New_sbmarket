from django.apps import apps
from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from django.templatetags.static import static

from .validators import UnicodeUsernameValidator

username_validator = UnicodeUsernameValidator()


class User(AbstractBaseUser):
    """
    사용자 모델.
    """

    username = models.CharField(
        max_length=150,
        unique=True,
        help_text="필수 입력 사항입니다. 150자 이하. 문자, 숫자 및 @/./+/-/_만 가능합니다.",
        validators=[username_validator],
        error_messages={"unique": "중복된 아이디입니다."},
        null=False,
        blank=False,
        db_column="userid",
    )
    nickname = models.CharField(
        max_length=50,
        db_column="nickname",
        help_text="사용자의 별명",
        null=False,
        blank=False,
    )
    name = models.CharField(
        max_length=50,
        db_column="name",
        help_text="사용자의 실제 이름",
        null=False,
        blank=False,
    )
    postcode = models.CharField(
        max_length=10,
        help_text="우편번호",
    )
    mainaddress = models.CharField(
        max_length=255,
        help_text="사용자의 기본 주소",
    )
    subaddress = models.CharField(
        max_length=255,
        help_text="사용자의 상세 주소",
    )
    extraaddress = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="사용자의 추가 주소 (선택 입력)",
    )
    birth = models.DateField(
        help_text="사용자의 생년월일",
    )
    email = models.EmailField(
        max_length=254,
        unique=False,
        null=False,
        blank=False,
        help_text="사용자의 이메일 주소",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="사용자 계정 생성 시간",
    )
    image = models.ImageField(
        upload_to="images/",
        blank=True,
        default="static/images/default_profile.jpg",
        help_text="사용자 프로필 이미지",
    )
    introduce = models.TextField(
        max_length=255,
        blank=True,
        null=True,
        help_text="사용자 자기소개 (선택 입력)",
    )
    total_score = models.FloatField(
        default=30,
        help_text="사용자의 초기 매너 점수",
    )
    followings = models.ManyToManyField(
        "self",
        symmetrical=False,
        related_name="followers",
        blank=True,
        help_text="사용자가 팔로우한 사용자 목록",
    )

    def get_profile_image_url(self):
        """
        프로필 이미지 URL 반환.
        """
        return self.image.url if self.image else static("images/default_profile.jpg")

    def handle_profile_image(self, remove_image, new_image):
        """
        프로필 이미지 삭제 또는 업데이트 로직.
        """
        if remove_image == "true" and self.image:
            self.image.delete()

        if new_image:
            self.image = new_image

    def deactivate_account(self):
        """
        계정 비활성화 처리 및 작성한 게시글 삭제.
        """
        self.is_active = False
        self.save()

        Product = apps.get_model("backend_products", "Product")
        Product.objects.filter(author=self).delete()

    def __str__(self):
        return self.username
