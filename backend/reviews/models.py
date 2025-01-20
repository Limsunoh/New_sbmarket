from django.db import models
from multiselectfield import MultiSelectField

# 체크리스트 옵션 정의
CHECKLIST_OPTIONS = (
    ("품질이 우수해요", "품질이 우수해요"),
    ("합리적인 가격이에요", "합리적인 가격이에요"),
    ("내구성이 뛰어나요", "내구성이 뛰어나요"),
    ("친절하고 매너가 좋아요", "친절하고 매너가 좋아요"),
    ("거래약속을 잘 지켜요", "거래약속을 잘 지켜요"),
    ("사진과 너무 달라요", "사진과 너무 달라요"),
    ("돈이 아까워요", "돈이 아까워요"),
    ("못 쓸 걸 팔았어요", "못 쓸 걸 팔았어요"),
    ("불친절하게 느껴졌어요", "불친절하게 느껴졌어요"),
    ("시간을 안 지켜요", "시간을 안 지켜요"),
)

# 점수 매핑 딕셔너리
SCORE_MAPPING = {
    "품질이 우수해요": 0.5,
    "합리적인 가격이에요": 0.5,
    "내구성이 뛰어나요": 0.5,
    "친절하고 매너가 좋아요": 0.5,
    "거래약속을 잘 지켜요": 0.5,
    "사진과 너무 달라요": -1,
    "돈이 아까워요": -1,
    "못 쓸 걸 팔았어요": -1,
    "불친절하게 느껴졌어요": -1,
    "시간을 안 지켜요": -1,
}


class Review(models.Model):
    """
    리뷰 모델.
    """

    author = models.ForeignKey(
        "backend_accounts.User",
        related_name="reviews",
        on_delete=models.CASCADE,
    )
    product = models.OneToOneField(
        "backend_products.Product",
        related_name="reviewed_product",
        on_delete=models.CASCADE,
    )
    checklist = MultiSelectField(choices=CHECKLIST_OPTIONS)
    additional_comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    score = models.FloatField(default=0)
    is_deleted = models.BooleanField(default=False)
    is_score_assigned = models.BooleanField(default=False)

    def calculate_score(self):
        """
        체크리스트를 기반으로 총 점수를 계산합니다.
        """
        return sum(SCORE_MAPPING.get(choice, 0) for choice in self.checklist)

    @classmethod
    def create_review(cls, author, product, checklist, additional_comments):
        """
        리뷰 생성 메서드.

        - 리뷰 작성 여부와 구매자 여부를 확인한 뒤 생성.
        """
        if hasattr(product, "reviewed_product"):
            raise ValueError("이 상품에는 이미 리뷰가 작성되었습니다.")

        chat_room = product.chatrooms.filter(buyer=author, status__is_sold=True).first()
        if not chat_room:
            raise ValueError("리뷰는 해당 상품의 구매자만 작성할 수 있습니다.")

        # 리뷰 생성 및 점수 반영
        review = cls(
            author=author,
            product=product,
            checklist=checklist,
            additional_comments=additional_comments,
        )
        review.score = review.calculate_score()
        review.is_score_assigned = True
        review.save()
        return review

    def delete(self, *args, **kwargs):
        """
        리뷰 삭제 메서드.

        - 실제로 삭제하지 않고 `is_deleted`를 True로 설정.
        """
        self.is_deleted = True
        self.save()

    def __str__(self):
        return f"{self.author.username} 의 {self.product.title} 에 대한 리뷰입니다"
