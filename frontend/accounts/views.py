from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from backend.accounts.models import User


class SignupPageView(TemplateView):
    """
    회원가입 페이지 템플릿 뷰.

    - 회원가입을 위한 템플릿을 렌더링합니다.
    """

    template_name = "signup.html"


class LoginPageView(TemplateView):
    """
    로그인 페이지 템플릿 뷰.

    - 로그인을 위한 템플릿을 렌더링합니다.
    """

    template_name = "login.html"


class ProfileView(TemplateView):
    """
    프로필 페이지 템플릿 뷰.

    - 사용자의 프로필 정보를 표시하는 템플릿을 렌더링합니다.
    """

    template_name = "profile.html"


class ProfileEditView(TemplateView):
    """
    프로필 수정 페이지 템플릿 뷰.

    - 사용자가 프로필 정보를 수정할 수 있는 템플릿을 렌더링합니다.
    """

    template_name = "profile_edit.html"


class ChangePasswordPageView(TemplateView):
    """
    비밀번호 변경 페이지 템플릿 뷰.

    - 사용자가 비밀번호를 변경할 수 있는 템플릿을 렌더링합니다.
    """

    template_name = "change_password.html"


class FollowingsPageView(TemplateView):
    """
    팔로잉 목록 페이지 템플릿 뷰.

    - 특정 사용자가 팔로잉하고 있는 사용자 목록을 표시합니다.
    """

    template_name = "followings.html"

    def get_context_data(self, **kwargs):
        """
        컨텍스트 데이터에 팔로잉 사용자 목록과 사용자 정보를 추가합니다.
        """
        context = super().get_context_data(**kwargs)
        username = self.kwargs.get("username")
        profile_user = get_object_or_404(User, username=username)
        context["profile_user"] = profile_user
        context["followings"] = profile_user.followings.all()
        return context


class FollowersPageView(TemplateView):
    """
    팔로워 목록 페이지 템플릿 뷰.

    - 특정 사용자를 팔로우하는 사용자 목록을 표시합니다.
    """

    template_name = "followers.html"

    def get_context_data(self, **kwargs):
        """
        컨텍스트 데이터에 팔로워 사용자 목록과 사용자 정보를 추가합니다.
        """
        context = super().get_context_data(**kwargs)
        username = self.kwargs.get("username")
        profile_user = get_object_or_404(User, username=username)
        context["profile_user"] = profile_user
        context["followers"] = profile_user.followers.all()
        return context


class LikeProductsPageView(TemplateView):
    """
    찜한 상품 목록 페이지 템플릿 뷰.

    - 사용자가 찜한 상품 목록을 표시합니다.
    """

    template_name = "liked_products.html"

    def get_context_data(self, **kwargs):
        """
        컨텍스트 데이터에 찜한 상품과 사용자 정보를 추가합니다.
        """
        context = super().get_context_data(**kwargs)
        username = self.kwargs.get("username")
        profile_user = get_object_or_404(User, username=username)
        context["profile_user"] = profile_user
        return context


class UserProductsListPageView(TemplateView):
    """
    사용자가 작성한 상품 목록 페이지 템플릿 뷰.

    - 특정 사용자가 작성한 상품 목록을 표시합니다.
    """

    template_name = "user_products.html"

    def get_context_data(self, **kwargs):
        """
        컨텍스트 데이터에 작성한 상품 목록과 사용자 정보를 추가합니다.
        """
        context = super().get_context_data(**kwargs)
        username = self.kwargs.get("username")
        profile_user = get_object_or_404(User, username=username)
        context["profile_user"] = profile_user
        return context


class PurchaseHistoryListViewTemplate(TemplateView):
    """
    구매한 제품 목록 페이지 템플릿 뷰.

    - 사용자가 구매한 제품 목록을 표시합니다.
    """

    template_name = "purchase_history_list.html"

    def get_context_data(self, **kwargs):
        """
        컨텍스트 데이터에 구매한 제품과 사용자 정보를 추가합니다.
        """
        context = super().get_context_data(**kwargs)
        username = self.kwargs.get("username")
        profile_user = get_object_or_404(User, username=username)
        context["profile_user"] = profile_user
        return context


class UserReviewListViewTemplate(TemplateView):
    """
    작성한 후기 목록 페이지 템플릿 뷰.

    - 사용자가 작성한 후기를 표시합니다.
    """

    template_name = "user_review_list.html"

    def get_context_data(self, **kwargs):
        """
        컨텍스트 데이터에 작성한 후기와 사용자 정보를 추가합니다.
        """
        context = super().get_context_data(**kwargs)
        username = self.kwargs.get("username")
        profile_user = get_object_or_404(User, username=username)
        context["profile_user"] = profile_user
        return context


class ReceivedReviewListViewTemplate(TemplateView):
    """
    받은 후기 목록 페이지 템플릿 뷰.

    - 사용자가 받은 후기를 표시합니다.
    """

    template_name = "received_review_list.html"

    def get_context_data(self, **kwargs):
        """
        컨텍스트 데이터에 받은 후기와 사용자 정보를 추가합니다.
        """
        context = super().get_context_data(**kwargs)
        username = self.kwargs.get("username")
        profile_user = get_object_or_404(User, username=username)
        context["profile_user"] = profile_user
        return context
