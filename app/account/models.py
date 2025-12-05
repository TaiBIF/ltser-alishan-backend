from django.conf import settings
from django.db import models


class UserAuthProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="auth_profile",
    )
    # 是否是首次透過 Google 建立這個帳號
    is_google_created = models.BooleanField(default=False)

    # 記錄 Google 的 sub（user 的唯一 ID）
    google_sub = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"AuthProfile<{self.user.email}>"
