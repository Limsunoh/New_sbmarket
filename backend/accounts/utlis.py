from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

RefreshToken = TokenObtainPairSerializer


class TokenManager:
    def __init__(self, user):
        self.user = user
        self.refresh = RefreshToken.for_user(user)

    def get_tokens(self):
        return {
            "refresh": str(self.refresh),
            "access": str(self.refresh.access_token),
        }
