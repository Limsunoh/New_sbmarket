from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from django.templatetags.static import static

from .validators import UnicodeUsernameValidator

username_validator = UnicodeUsernameValidator()


class User(AbstractBaseUser):
    """
    사용자 모델.

    - 사용자명, 닉네임, 주소, 프로필 이미지, 팔로우 기능 등을 포함합니다.
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
        프로필 이미지 URL을 반환.

        - 사용자가 프로필 이미지를 업로드하지 않았을 경우 기본 이미지를 반환합니다.
        """
        return self.image.url if self.image else static("images/default_profile.jpg")

    def __str__(self):
        """
        문자열 표현.

        - 사용자명을 기준으로 사용자 객체를 문자열로 나타냅니다.
        """
        return self.username
