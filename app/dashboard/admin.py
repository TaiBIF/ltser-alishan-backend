from django.contrib import admin
from django.utils.html import format_html

from .models import *


class CouEventImageInline(admin.TabularInline):
    model = CouEventImage
    extra = 1
    can_delete = True
    fields = (
        "preview",
        "image",
    )
    readonly_fields = ("preview",)

    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:80px;" />', obj.image.url)
        return "-"


@admin.register(CouEventType)
class CouEventTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "key", "name")
    list_filter = ("name",)
    search_fields = ("key", "name")
    ordering = ("id",)


@admin.register(CouEvent)
class CouEventAdmin(admin.ModelAdmin):
    list_display = ("id", "date", "location", "get_types", "images_count", "created_at")
    list_filter = ("types", "date", "location")
    search_fields = ("location", "content", "types__name", "types__key")
    date_hierarchy = "date"
    ordering = ("-date",)
    readonly_fields = ("created_at", "updated_at")
    inlines = [CouEventImageInline]

    def images_count(self, obj):
        return obj.images.count()

    @admin.display(description="types")
    def get_types(self, obj):
        return ", ".join(t.name for t in obj.types.all())

    images_count.short_description = "image counts"


@admin.register(Introduction)
class IntroductionAdmin(admin.ModelAdmin):
    list_display = ("id", "type", "name", "created_at")
    list_filter = ("type",)
    search_fields = ("type", "name")
    ordering = ("id",)
    readonly_fields = ("created_at", "updated_at")


class NewsCoverImageInline(admin.StackedInline):
    model = NewsCoverImage
    fk_name = "news_cover"
    extra = 1
    max_num = 1
    can_delete = True
    fields = (
        "preview",
        "image",
    )
    readonly_fields = ("preview",)

    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:80px;" />', obj.image.url)
        return "-"


class NewsImageInline(admin.TabularInline):
    model = NewsImage
    extra = 1
    can_delete = True
    fields = (
        "preview",
        "image",
    )
    readonly_fields = ("preview",)

    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:80px;" />', obj.image.url)
        return "-"


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ("id", "get_types", "title", "created_at")
    list_filter = ("types",)
    search_fields = ("types", "title", "content", "types__name", "types__key")
    ordering = ("id",)
    readonly_fields = ("created_at", "updated_at")
    inlines = [NewsCoverImageInline, NewsImageInline]

    @admin.display(description="types")
    def get_types(self, obj):
        return ", ".join(t.name for t in obj.types.all())


@admin.register(NewsType)
class NewsTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "key", "name")
    list_filter = ("name",)
    search_fields = ("key", "name")
    ordering = ("id",)


@admin.register(Faq)
class FaqAdmin(admin.ModelAdmin):
    list_display = ("id", "question")
    list_filter = ("types",)
    search_fields = ("types", "question")
    ordering = ("id",)
    readonly_fields = ("created_at", "updated_at")

    @admin.display(description="types")
    def get_types(self, obj):
        return ", ".join(t.name for t in obj.types.all())


@admin.register(FaqType)
class FaqTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "key", "name")
    list_filter = ("name",)
    search_fields = ("key", "name")
    ordering = ("id",)


@admin.register(Literature)
class LiteratureAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "get_types",
        "date",
        "author",
        "affiliation",
    )
    list_filter = ("types", "date", "author", "affiliation")
    search_fields = ("types", "title", "author", "affiliation")
    ordering = ("id",)
    readonly_fields = ("created_at", "updated_at")

    @admin.display(description="types")
    def get_types(self, obj):
        return ", ".join(t.name for t in obj.types.all())


@admin.register(LiteratureType)
class LiteratureTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "key", "name")
    list_filter = ("name",)
    search_fields = ("key", "name")
    ordering = ("id",)


@admin.register(FormLink)
class FormLinkAdmin(admin.ModelAdmin):
    list_display = ("id", "title")
    list_filter = ("title",)
    search_fields = ("title",)
    ordering = ("id",)


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "role",
        "university",
        "sort_order",
    )

    list_filter = (
        "university",
        "role",
    )

    search_fields = (
        "name",
        "role",
        "mail",
        "university",
        "department",
        "position",
    )

    ordering = ("sort_order", "id")
