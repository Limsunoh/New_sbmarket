from django.core.cache import cache
from django.db import models

from backend.accounts.models import User

from .validators import HashtagValidator


class Hashtag(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True,
        validators=[HashtagValidator()],
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

    def increment_hits(self, user=None, viewed_products_key=None):
        """
        조회수 증가 로직
        :param user: 현재 사용자 (로그인 상태일 경우)
        :param viewed_products_key: 사용자별 캐시 키 (로그인 상태일 경우)
        """
        if user:  # 로그인 사용자
            if viewed_products_key:
                viewed_products = cache.get(viewed_products_key, [])
                if self.id not in viewed_products:
                    self.hits += 1
                    self.save(update_fields=["hits"])
                    viewed_products.append(self.id)
                    cache.set(viewed_products_key, viewed_products, timeout=60 * 60 * 24)  # 24시간 동안 저장
        else:  # 비로그인 사용자
            # 비로그인 사용자의 조회 목록은 쿠키에서 가져옴
            if "viewed_products" in self.request.COOKIES:
                viewed_products = self.request.COOKIES["viewed_products"].split(",")
            else:
                viewed_products = []

            if str(self.id) not in viewed_products:
                self.hits += 1
                self.save(update_fields=["hits"])
                viewed_products.append(str(self.id))
                self.request._response.set_cookie("viewed_products", ",".join(viewed_products), max_age=60 * 60 * 24)

    def __str__(self):
        return f"User:{self.author} (Status:{self.status})"


class Image(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image_url = models.ImageField(upload_to="images/")
