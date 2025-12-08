from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from .views import EmailTokenObtainPairView, GoogleLoginView, UserMeView

urlpatterns = [
    path("token/", EmailTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("google-login/", GoogleLoginView.as_view(), name="google-login"),
    path("user/me/", UserMeView.as_view(), name="user-me"),
]
