from django.conf import settings
from django.contrib.auth import get_user_model

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

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
    2. 用 email 找/建 user
    3. 發 JWT access / refresh 回前端
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

        # 找看看是否已有此 email 的 user
        user = User.objects.filter(email__iexact=email).first()

        # 沒有就建立一個 user（用 email 當 username）
        if not user:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=User.objects.make_random_password(),
                first_name=name,
            )

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
