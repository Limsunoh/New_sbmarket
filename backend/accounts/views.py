from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import (
    CreateAPIView,
    GenericAPIView,
    ListAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from backend.accounts.models import User
from backend.accounts.serializers import (
    ActivateUserSerializer,
    ChangePasswordSerializer,
    CustomTokenObtainPairSerializer,
    UserChangeSerializer,
    UserListSerializer,
    UserProfileSerializer,
    UserSerializer,
)
from backend.products.models import Product
from backend.products.serializers import ProductListSerializer, PurchaseSerializer
from backend.reviews.models import Review
from backend.reviews.serializers import ReviewSerializer


# 유저 생성 API
class UserCreateView(CreateAPIView):
    """
    사용자 생성 및 이메일 인증을 처리하는 뷰.

    - 회원가입 요청을 처리하고 사용자 데이터를 생성합니다.
    - 이메일 인증을 위한 사용자 활성화 로직도 포함됩니다.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """
        회원가입 요청 처리.

        - 클라이언트에서 보낸 데이터를 검증한 후 새로운 사용자를 생성합니다.
        - 데이터가 유효하지 않으면 400 Bad Request를 반환합니다.

        Args:
            request: 클라이언트 요청 객체.
        """
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ActivateUser(GenericAPIView):
    """
    사용자 활성화를 처리하는 뷰.

    - 이메일 인증 링크를 통해 전달된 사용자 ID와 토큰을 검증합니다.
    - 인증이 완료되면 사용자의 상태를 활성화로 변경합니다.
    """

    serializer_class = ActivateUserSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """
        이메일 인증 처리.

        - 이메일 인증 링크를 통해 전달된 사용자 ID와 토큰을 검증합니다.
        - 인증이 완료되면 사용자의 상태를 활성화로 변경합니다.

        Args:
            request: 클라이언트 요청 객체.
        """
        serializer = ActivateUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            user.is_active = True
            user.save()
            return Response({"message": "이메일 인증이 완료되었습니다!"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    사용자 토큰 발급 뷰.

    - 사용자 로그인 요청을 처리하고, JWT 토큰을 발급합니다.
    - 사용자가 인증되지 않은 경우 401 Unauthorized를 반환합니다.
    """

    serializer_class = CustomTokenObtainPairSerializer


class UserProfileView(RetrieveUpdateDestroyAPIView):
    """
    사용자 프로필 조회, 수정 및 삭제 뷰.

    - GET: 프로필 조회
    - PATCH/PUT: 프로필 수정
    - DELETE: 계정 비활성화 및 작성한 게시글 삭제
    """

    queryset = User.objects.all()
    lookup_field = "username"
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        """
        요청에 따라 적절한 Serializer를 반환합니다.
        - GET 요청: UserProfileSerializer
        - PATCH/PUT 요청: UserChangeSerializer
        """
        if self.request.method == "GET":
            return UserProfileSerializer
        if self.request.method in ["PATCH", "PUT"]:
            return UserChangeSerializer
        return super().get_serializer_class()

    def update(self, request, *args, **kwargs):
        """
        사용자 프로필 업데이트.

        - 프로필 이미지 업로드 및 삭제 처리 포함.
        """
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        self.handle_profile_image(user, request)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def handle_profile_image(self, user, request):
        """
        프로필 이미지 업로드 및 삭제를 처리합니다.
        """
        if request.data.get("remove_image") == "true" and user.image:
            user.image.delete()

        if "image" in request.FILES:
            user.image = request.FILES["image"]

    def delete(self, request, *args, **kwargs):
        """
        사용자 계정 비활성화 및 작성 게시글 삭제.
        """
        user = self.get_object()
        if user != request.user:
            return Response(
                {"message": "삭제 처리할 권한이 없습니다."},
                status=status.HTTP_403_FORBIDDEN,
            )

        user.is_active = False
        Product.objects.filter(author=user).delete()
        user.save()
        return Response(
            {"message": "삭제 처리가 완료되었습니다."},
            status=status.HTTP_204_NO_CONTENT,
        )


class ChangePasswordView(GenericAPIView):
    """
    사용자 비밀번호 변경 뷰.
    - 인증된 사용자만 접근 가능.
    - 요청 데이터에서 새 비밀번호를 검증 후 저장.
    """

    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        """
        PATCH 요청을 처리하여 사용자 비밀번호를 변경합니다.
        """
        user = request.user
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user)
        return Response({"message": "비밀번호가 성공적으로 변경되었습니다."}, status=status.HTTP_200_OK)


class FollowView(GenericAPIView):
    """
    팔로우/언팔로우 및 팔로우 상태 확인 뷰.

    - GET: 특정 사용자를 팔로우하고 있는지 확인.
    - POST: 팔로우하거나 언팔로우를 처리.
    """

    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_field = "username"  # URL에서 username으로 조회

    def get(self, request, *args, **kwargs):
        """
        팔로우 상태 확인.

        - 요청자가 특정 사용자를 팔로우 중인지 확인.
        """
        user = self.get_object()  # 팔로우 대상 사용자
        is_following = request.user in user.followers.all()
        return Response({"is_following": is_following}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """
        팔로우/언팔로우 처리.

        - 요청자의 팔로우 상태를 반전시킵니다.
        """
        target_user = self.get_object()
        current_user = request.user

        if current_user in target_user.followers.all():
            target_user.followers.remove(current_user)
            return Response({"message": "unfollow했습니다."}, status=status.HTTP_200_OK)

        target_user.followers.add(current_user)
        return Response({"message": "follow했습니다."}, status=status.HTTP_200_OK)


class UserFollowingListAPIView(ListAPIView):
    """
    사용자의 팔로잉 목록 조회 API.
    """

    serializer_class = UserListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        username = self.kwargs.get("username")
        user = get_object_or_404(User, username=username)
        return user.followings.all()


class UserFollowerListAPIView(ListAPIView):
    """
    사용자의 팔로워 목록 조회 API.
    """

    serializer_class = UserListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        username = self.kwargs.get("username")
        user = get_object_or_404(User, username=username)
        return user.followers.all()


class LikeListForUserAPIView(ListAPIView):
    """
    사용자가 찜한 상품 목록 조회 API.
    """

    serializer_class = ProductListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        username = self.kwargs.get("username")
        user = get_object_or_404(User, username=username)
        return Product.objects.filter(likes=user)


class UserProductsListView(ListAPIView):
    """
    사용자가 작성한 상품 목록 조회 API.
    """

    serializer_class = ProductListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        username = self.kwargs.get("username")
        return Product.objects.filter(author__username=username)


class PurchaseHistoryListView(ListAPIView):
    """
    사용자의 구매 내역 조회 API.
    """

    serializer_class = PurchaseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Product.objects.filter(chatrooms__buyer=user, chatrooms__status__is_sold=True)


class UserReviewListView(ListAPIView):
    """
    사용자가 작성한 후기 목록 조회 API.
    """

    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        username = self.kwargs.get("username")
        user = get_object_or_404(User, username=username)
        return Review.objects.filter(author=user, is_deleted=False)


class ReceivedReviewListView(ListAPIView):
    """
    사용자가 받은 후기 목록 조회 API.
    - 매너점수 클릭 시 표시되는 후기들.
    """

    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        username = self.kwargs.get("username")
        user = get_object_or_404(User, username=username)
        return Review.objects.filter(product__author=user, is_deleted=False)
