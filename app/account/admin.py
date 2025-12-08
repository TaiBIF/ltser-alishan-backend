from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html

from .models import UserAuthProfile

User = get_user_model()

try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    # 有些情況可能還沒註冊，不影響
    pass


class UserAuthProfileInline(admin.StackedInline):
    model = UserAuthProfile
    extra = 0
    can_delete = False
    fk_name = "user"

    readonly_fields = ("created_at",)

    fieldsets = (
        (
            "Google Login Info",
            {
                "fields": (
                    "is_google_created",
                    "google_sub",
                    "role",
                    "created_at",
                )
            },
        ),
    )


# -------------------------------
# 自訂 User Admin
# -------------------------------
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    用 inline 的方式把 UserAuthProfile 加到 User 頁面。
    """

    inlines = [UserAuthProfileInline]

    list_display = (
        "id",
        "email",
        "username",
        "first_name",
        "user_role",
        "is_staff",
        "google_flag",
    )
    list_filter = ("is_staff", "is_superuser", "is_active", "auth_profile__role")
    search_fields = ("email", "username", "first_name", "auth_profile__role")
    ordering = ("id",)

    @admin.display(description="Google Created?")
    def google_flag(self, obj):
        """顯示是否為 Google 建立帳號"""
        if hasattr(obj, "auth_profile") and obj.auth_profile.is_google_created:
            return format_html('<span style="color:green;">Yes</span>')
        return format_html('<span style="color:#999;">No</span>')

    @admin.display(description="Role")
    def user_role(self, obj):
        if hasattr(obj, "auth_profile") and obj.auth_profile.role:
            return obj.auth_profile.role
        return "-"
