from django.core.validators import RegexValidator
from rest_framework import serializers

from .models import User

# Custom RegexValidator for password validation
password_regex_validator = RegexValidator(
    regex=r'^(?=.*[A-Za-z])(?=.*[\d])(?=.*[!@#$%^&*(),.?":{}|<>])(?!.*(.)\1\1).{10,}$',
    message="비밀번호는 최소 10자 이상이어야 하며, 숫자, 문자, 특수문자 중 2가지 이상을 포함해야 하고, 연속되는 동일 문자가 3회 이상 반복되지 않아야 합니다.",
)


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[password_regex_validator], required=True)
    check_password = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=True, allow_blank=False)
    email_code = serializers.IntegerField(write_only=True, required=True)
    postcode = serializers.CharField(required=False)
    mainaddress = serializers.CharField(required=False)
    subaddress = serializers.CharField(required=False)
    profile_image = serializers.SerializerMethodField()
    total_score = serializers.FloatField(read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "password",
            "check_password",
            "name",
            "nickname",
            "birth",
            "email",
            "postcode",
            "mainaddress",
            "subaddress",
            "extraaddress",
            "image",
            "profile_image",
            "introduce",
            "created_at",
            "total_score",
        )
        read_only_fields = ("id", "created_at", "total_score")
        write_only_fields = ("password", "check_password", "email_code", "image")

    def validate(self, data):
        # 비밀번호와 확인 비밀번호가 일치하는지 검사
        if data["password"] != data["check_password"]:
            raise serializers.ValidationError({"check_password": "비밀번호가 일치하지 않습니다."})
        return data

    def create(self, validated_data):
        validated_data.pop("check_password", None)
        validated_data.pop("email_code", None)
        image = validated_data.get("image", None)
        if not image:
            image = "frontend/images/default_profile_image.jpg"

        user = User(
            username=validated_data["username"],
            email=validated_data["email"],
            name=validated_data.get("name", ""),
            nickname=validated_data.get("nickname", ""),
            birth=validated_data.get("birth", None),
            postcode=validated_data.get("postcode", ""),
            mainaddress=validated_data.get("mainaddress"),
            subaddress=validated_data.get("subaddress"),
            image=image,
            introduce=validated_data.get("introduce", ""),
        )
        user.set_password(validated_data["password"])
        user.is_active = False
        user.total_score = 30  # 기본 점수 설정
        user.save()
        return user
