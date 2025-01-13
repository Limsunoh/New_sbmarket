from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import User
from .serializers import ActivateUserSerializer, UserSerializer


# 유저 생성 API
class UserCreateView(CreateAPIView, GenericAPIView):
    """
    사용자 생성 및 이메일 인증을 처리하는 뷰.

    - 회원가입 요청을 처리하고 사용자 데이터를 생성합니다.
    - 이메일 인증을 위한 사용자 활성화 로직도 포함됩니다.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
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

    @action(detail=False, methods=["post"], url_path="activate-user")
    def activate_user(self, request, *args, **kwargs):
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
