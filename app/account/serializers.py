from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.db.models import Q
from .models import UserAuthProfile

User = get_user_model()


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    email = serializers.EmailField(write_only=True, required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # simplejwt 的父類預設會動態加上 self.username_field(= 'username') 欄位且 required=True
        # 我們改成不強制填，因為我們要用 email 來填入它
        self.fields[self.username_field].required = False

    def validate(self, attrs):
        # 從 attrs 或 raw initial_data 取 email
        email = (
            attrs.get("email") or self.initialization_data.get("email")
            if hasattr(self, "initialization_data")
            else None
        )
        if email is None:
            # 某些 DRF 版本 attrs 不會帶未宣告欄位，這裡保險處理
            email = self.initial_data.get("email")

        password = attrs.get("password")

        if not email or not password:
            raise serializers.ValidationError({"detail": "email 與 password 為必填"})

        # 我們註冊時把 username = email，所以把 username 欄位值設為 email
        # 讓父類沿用「以 username + password 認證」的流程 (無需自訂 AUTH_BACKENDS)
        attrs[self.username_field] = email

        return super().validate(attrs)


class RegisterSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={"input_type": "password"})
    password2 = serializers.CharField(write_only=True, style={"input_type": "password"})

    def validate_email(self, value):
        value = value.strip().lower()

        # 同一個 email 只允許一個帳號（不區分密碼/Google）
        user = User.objects.filter(
            Q(email__iexact=value) | Q(username__iexact=value)
        ).first()

        if user:
            raise serializers.ValidationError(
                "此 Email 已註冊，請直接登入，或使用「忘記密碼」重設密碼。"
            )

        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password2": "兩次密碼不一致"})
        # Django 內建密碼規則（會丟出多條訊息陣列）
        try:
            validate_password(attrs["password"])
        except serializers.ValidationError as e:
            raise serializers.ValidationError({"password": e.messages})
        return attrs

    def create(self, validated_data):
        name = validated_data["name"].strip()
        email = validated_data["email"].strip().lower()
        password = validated_data["password"]

        user = User.objects.create_user(
            username=email,  # email 直接當作 username
            email=email,
            password=password,
            first_name=name,  # name 直接放到 first_name 中不拆分
        )

        UserAuthProfile.objects.get_or_create(user=user)

        return user


class UserMeSerializer(serializers.ModelSerializer):
    role = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ["username", "first_name", "role"]
        read_only_fields = ["username"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        profile = getattr(instance, "auth_profile", None)
        data["role"] = getattr(profile, "role", "") if profile else ""
        return data

    def update(self, instance, validated_data):
        role = validated_data.pop("role", None)

        # 先更新 User 本體欄位
        instance = super().update(instance, validated_data)

        # 再更新 Auth Profile.role
        profile = getattr(instance, "auth_profile", None)
        if profile:
            if role is not None:
                profile.role = role
                profile.save()

        return instance
