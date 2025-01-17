from django.db import models

from backend.accounts.models import User

from .validators import HashtagValidator


class Hashtag(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True,
        validators=[HashtagValidator()],  # RegexValidator 적용
    )

    def __str__(self):
        return self.name


class Product(models.Model):
    CHOICE_PRODUCT = [
        ("sell", "판매중"),
        ("reservation", "예약중"),
        ("complete", "판매완료"),
    ]
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="author_product")  # 작성자
    title = models.CharField(max_length=50)
    content = models.TextField()
    price = models.DecimalField(max_digits=20, decimal_places=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=50, choices=CHOICE_PRODUCT, default="sell")
    hits = models.PositiveIntegerField(blank=True, default=0)  # 조회수
    likes = models.ManyToManyField(User, related_name="like_products", blank=True)  # 좋아요
    tags = models.ManyToManyField(Hashtag, related_name="products", blank=True)  # 해시태그

    def __str__(self):
        return f"User:{self.author} (Status:{self.status})"


class Image(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image_url = models.ImageField(upload_to="images/")
