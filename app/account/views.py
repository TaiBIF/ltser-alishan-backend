from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Q

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from .models import UserAuthProfile
from .serializers import RegisterSerializer, EmailTokenObtainPairSerializer


User = get_user_model()


class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "註冊成功"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GoogleLoginView(APIView):
    """
    前端丟 Google ID token (credential) 進來，
    這裡負責：
    1. 驗證 token 是否有效
    2. 用 email 找/建 user（同一個 email 只會有一個 user）
    3. 發 JWT access / refresh 回前端

    策略：
    - 如果這個 email 已經註冊（一般註冊或之前用 Google 建立），
      就直接登入同一個 User → 同一個帳號可以同時用密碼 & Google 登入。
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        credential = request.data.get("credential")
        if not credential:
            return Response(
                {"detail": "缺少 Google credential"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not getattr(settings, "GOOGLE_CLIENT_ID", None):
            return Response(
                {"detail": "後端尚未設定 GOOGLE_CLIENT_ID"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # 驗證 Google ID Token
        try:
            idinfo = id_token.verify_oauth2_token(
                credential,
                google_requests.Request(),
                settings.GOOGLE_CLIENT_ID,
            )
        except ValueError:
            # 驗證失敗（token 過期、不合法、client_id 不符...）
            return Response(
                {"detail": "無效的 Google token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        email = idinfo.get("email")
        email_verified = idinfo.get("email_verified")
        name = idinfo.get("name") or ""

        if not email or not email_verified:
            return Response(
                {"detail": "無法取得已驗證的 Email"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        email = email.strip().lower()

        # 用 email 找既有 user
        user = User.objects.filter(
            Q(email__iexact=email) | Q(username__iexact=email)
        ).first()

        # 沒有就建立一個 user（用 email 當 username）
        created_by_google = False
        if not user:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=User.objects.make_random_password(),
                first_name=name,
            )
            created_by_google = True

        # 更新 / 建立這個使用者的 auth_profile
        profile, _ = UserAuthProfile.objects.get_or_create(user=user)

        # 只要曾經是用 Google 建立的，就標記 True（之後不會改回 False）
        if created_by_google and not profile.is_google_created:
            profile.is_google_created = True

        # 記錄 Google 的 sub（只有 Google 會給的唯一 ID）
        sub = idinfo.get("sub")
        if sub and profile.google_sub != sub:
            profile.google_sub = sub

        profile.save()

        # 發 SimpleJWT token
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        return Response(
            {
                "access": str(access),
                "refresh": str(refresh),
            },
            status=status.HTTP_200_OK,
        )
