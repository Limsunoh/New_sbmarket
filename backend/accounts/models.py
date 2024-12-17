from django.db import models

from django.contrib.auth.models import AbstractBaseUser

class User(AbstractBaseUser):
    nickname = models.CharField(max_length=50, db_column='nickname', help_text='nickname', null=False, blank=False)
    name = models.CharField(max_length=50, db_column='name', help_text='name', null=False, blank=False)