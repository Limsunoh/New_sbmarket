from django.contrib.auth.models import AbstractBaseUser
from django.db import models

from .validators import UnicodeUsernameValidator

username_validator = UnicodeUsernameValidator()


class User(AbstractBaseUser):
    username = models.CharField(
        max_length=150,
        unique=True,
        help_text="필수 입력 사항입니다. 150자 이하. 문자, 숫자 및 @/./+/-/_만 가능합니다.",
        validators=[username_validator],
        error_messages="unique":"중복된 아이디 입니다.",
        null=False,
        blank=False,
        db_column="userid",
    )
    nickname = models.CharField(
        max_length=50,
        db_column="nickname",
        help_text="nickname",
        null=False,
        blank=False,
    )
    name = models.CharField(
        max_length=50, db_column="name", help_text="실제이름", null=False, blank=False
    )
    
