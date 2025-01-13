from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from django.templatetags.static import static

from .validators import UnicodeUsernameValidator

username_validator = UnicodeUsernameValidator()


class User(AbstractBaseUser):
    username = models.CharField(
        max_length=150,
        unique=True,
        help_text=("필수 입력 사항입니다. 150자 이하. 문자, 숫자 및 @/./+/-/_만 가능합니다."),
        validators=[username_validator],
        error_messages={"중복된 아이디 입니다."},
        null=False,
        blank=False,
        db_column="userid",
    )
    nickname = models.CharField(max_length=50, db_column="nickname", help_text="nickname", null=False, blank=False)
    name = models.CharField(max_length=50, db_column="name", help_text="실제이름", null=False, blank=False)
    postcode = models.CharField(max_length=10)
    mainaddress = models.CharField(max_length=255)
    subaddress = models.CharField(max_length=255)
    extraaddress = models.CharField(max_length=255, blank=True, null=True)
    birth = models.DateField()
    email = models.EmailField(max_length=30, unique=False, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to="images/", blank=True, default="static/images/default_profile.jpg")
    introduce = models.TextField(max_length=255, blank=True, null=True)
    total_score = models.FloatField(default=30)
    followings = models.ManyToManyField("self", symmetrical=False, related_name="followers", blank=True)

    def get_profile_image_url(self):
        if self.image:
            return self.image.url
        else:
            return static("images/default_profile.jpg")
