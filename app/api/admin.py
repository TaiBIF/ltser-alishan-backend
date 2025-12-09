from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
import os

from .models import DownloadRequest


@admin.register(DownloadRequest)
class DownloadRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "email",
        "first_name",
        "location_display",
        "year",
        "items_short",
        "status_badge",
        "email_sent_flag",
        "created_at",
        "finished_at",
    )
    list_filter = (
        "status",
        "email_sent",
        "year",
        "created_at",
        "finished_at",
        "role",
    )
    search_fields = (
        "email",
        "first_name",
        "role",
        "location_id",
        "location_name",
    )
    date_hierarchy = "created_at"
    ordering = ("-created_at",)

    readonly_fields = (
        "email",
        "location_id",
        "location_name",
        "year",
        "items",
        "created_at",
        "finished_at",
        "zip_path",
        "error_message",
        "email_sent",
        "email_error",
    )

    fieldsets = (
        (
            "申請人資訊",
            {
                "fields": (
                    "email",
                    "first_name",
                    "role",
                    "reason",
                )
            },
        ),
        (
            "下載條件",
            {
                "fields": (
                    "location_id",
                    "location_name",
                    "year",
                    "items",
                )
            },
        ),
        (
            "處理狀態",
            {
                "fields": (
                    "status",
                    "created_at",
                    "finished_at",
                    "zip_path",
                    "error_message",
                )
            },
        ),
        (
            "寄信狀態",
            {
                "fields": (
                    "email_sent",
                    "email_error",
                )
            },
        ),
    )

    # -------------------------
    # 自訂欄位顯示
    # -------------------------

    @admin.display(description="Role")
    def user_role(self, obj):
        return obj.role or "-"

    @admin.display(description="Location ID")
    def location_display(self, obj):
        if obj.location_name:
            return f"{obj.location_name} ({obj.location_id})"
        return obj.location_id

    @admin.display(description="OBSERVATION ITEMS")
    def items_short(self, obj):
        if not obj.items:
            return "-"
        if isinstance(obj.items, list):
            text = "、".join(obj.items)
        else:
            # 如果不是 list（例如字串），保底處理
            text = str(obj.items)

        return text if len(text) <= 30 else text[:27] + "..."

    @admin.display(description="STATUS")
    def status_badge(self, obj):
        color_map = {
            "pending": "#999999",
            "processing": "#007bff",
            "done": "#28a745",
            "failed": "#dc3545",
            "expired": "#ffa500",
        }
        label_map = dict(DownloadRequest.STATUS_CHOICES)

        color = color_map.get(obj.status, "#666666")
        label = label_map.get(obj.status, obj.status)

        return format_html(
            """
            <span style="
                padding:2px 6px;
                border-radius:4px;
                background-color:{};
                color:white;
                font-size:12px;
            ">{}</span>
            """,
            color,
            label,
        )

    @admin.display(boolean=True, description="Email Sent")
    def email_sent_flag(self, obj):
        return obj.email_sent
