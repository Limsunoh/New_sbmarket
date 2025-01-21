from django.views.generic import TemplateView

from backend.reviews.models import CHECKLIST_OPTIONS


class ReviewCreateView(TemplateView):
    """
    리뷰 작성 페이지 템플릿 뷰.

    - 특정 상품에 대한 리뷰를 작성할 수 있는 템플릿을 렌더링합니다.
    - 상품 ID와 리뷰 체크리스트 옵션을 컨텍스트에 추가합니다.
    """

    template_name = "review_create.html"

    def get_context_data(self, **kwargs):
        """
        컨텍스트 데이터에 상품 ID와 리뷰 체크리스트 옵션을 추가합니다.

        Args:
            **kwargs: URL에서 전달된 추가 매개변수.
        """
        context = super().get_context_data(**kwargs)
        context["product_id"] = kwargs.get("product_id")  # URL에서 전달된 product_id
        context["checklist_options"] = CHECKLIST_OPTIONS  # 리뷰 체크리스트 옵션 추가
        return context
