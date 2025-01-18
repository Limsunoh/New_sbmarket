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

# 점수 매핑 딕셔너리 (CHECKLIST_OPTIONS와 동일한 키 사용)
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

    - 작성자와 상품 간 1:1 관계로 연결.
    - 체크리스트와 추가 코멘트를 통해 리뷰 작성.
    """

    author = models.ForeignKey(
        "backend_accounts.User",
        related_name="reviews",
        on_delete=models.CASCADE,
        help_text="리뷰를 작성한 사용자",
    )
    product = models.OneToOneField(
        "backend_products.Product",
        related_name="reviewed_product",
        on_delete=models.CASCADE,
        help_text="리뷰가 작성된 상품",
    )
    checklist = MultiSelectField(
        choices=CHECKLIST_OPTIONS,
        help_text="리뷰 체크리스트 (다중 선택 가능)",
    )
    additional_comments = models.TextField(blank=True, help_text="추가 코멘트")
    created_at = models.DateTimeField(auto_now_add=True, help_text="리뷰 작성일")
    score = models.FloatField(default=0, help_text="리뷰 점수")

    # 상태 필드
    is_deleted = models.BooleanField(default=False, help_text="리뷰 삭제 여부 (삭제 후 재작성 방지)")
    is_score_assigned = models.BooleanField(default=False, help_text="리뷰 점수 할당 여부 (최초 저장 시에만 반영)")

    def calculate_score(self):
        """
        체크리스트를 기반으로 총 점수를 계산합니다.
        """
        return sum(SCORE_MAPPING.get(choice, 0) for choice in self.checklist)

    def save(self, *args, **kwargs):
        """
        리뷰 저장 메서드.

        - 점수를 최초로 계산 및 반영.
        - 상품 작성자의 총점(total_score)을 업데이트.
        """
        if not self.is_score_assigned:
            self.score = self.calculate_score()
            seller = self.product.author
            seller.total_score += self.score
            seller.save()
            self.is_score_assigned = True
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        리뷰 삭제 메서드.

        - 리뷰를 실제로 삭제하지 않고, `is_deleted` 플래그를 True로 설정.
        """
        self.is_deleted = True
        self.save()

    def __str__(self):
        return f"{self.author.username} 의 {self.product.title} 에 대한 리뷰입니다"
