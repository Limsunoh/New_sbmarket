from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, TemplateView

from backend.products.models import Product


class HomePageView(TemplateView):
    """
    홈 페이지 템플릿 뷰.

    - 상품 목록을 표시하기 위한 기본 템플릿을 렌더링합니다.
    """

    template_name = "home.html"


class ProductDetailPageView(DetailView):
    """
    상품 세부 정보 템플릿 뷰.

    - 특정 상품의 세부 정보를 표시합니다.
    - 상품 이미지와 함께 추가 컨텍스트 데이터를 제공합니다.
    """

    model = Product
    template_name = "product_detail.html"
    context_object_name = "product"

    def get_context_data(self, **kwargs):
        """
        컨텍스트 데이터에 상품 이미지를 추가합니다.
        """
        context = super().get_context_data(**kwargs)
        context["images"] = self.object.images.all()
        return context


class ProductCreateView(TemplateView):
    """
    상품 작성 페이지 템플릿 뷰.

    - 상품을 작성할 수 있는 입력 양식을 포함한 템플릿을 렌더링합니다.
    """

    template_name = "product_create.html"


class ProductEditPageView(TemplateView):
    """
    상품 수정 페이지 템플릿 뷰.

    - 특정 상품의 정보를 수정하기 위한 템플릿을 렌더링합니다.
    """

    template_name = "product_edit.html"

    def get_context_data(self, **kwargs):
        """
        컨텍스트 데이터에 수정할 상품 정보를 추가합니다.
        """
        context = super().get_context_data(**kwargs)
        product = get_object_or_404(Product, pk=self.kwargs["pk"])
        context["product"] = product
        return context


class ChatRoomListHTMLView(TemplateView):
    """
    채팅방 리스트 페이지 템플릿 뷰.

    - 사용자가 참여 중인 채팅방 목록을 표시합니다.
    """

    template_name = "chat_room_list.html"


class ChatRoomDetailHTMLView(TemplateView):
    """
    채팅방 상세 페이지 템플릿 뷰.

    - 특정 상품과 연결된 채팅방의 상세 정보를 표시합니다.
    - 채팅방 ID, 상품 ID, 상품 제목과 같은 정보를 컨텍스트에 추가합니다.
    """

    template_name = "chat_room.html"

    def get_context_data(self, **kwargs):
        """
        컨텍스트 데이터에 채팅방 및 상품 정보를 추가합니다.
        """
        context = super().get_context_data(**kwargs)
        product = get_object_or_404(Product, id=self.kwargs["product_id"])
        context["room_id"] = self.kwargs["room_id"]
        context["product_id"] = self.kwargs["product_id"]
        context["product_title"] = product.title
        return context
