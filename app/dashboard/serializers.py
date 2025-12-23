from rest_framework import serializers
from .models import *


class IntroductionSerializer(serializers.ModelSerializer):
    media = serializers.ImageField(required=False, allow_null=True, write_only=True)
    # 回傳給前端看的絕對網址
    media_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Introduction
        fields = [
            "id",
            "type",
            "name",
            "name_en",
            "content",
            "content_en",
            "media",  # 上傳用
            "media_url",  # 顯示用
        ]

    def get_media_url(self, obj):
        if not obj.media:
            return None
        request = self.context.get("request")
        url = obj.media.url
        return request.build_absolute_uri(url) if request else url


class CouEventTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CouEventType
        fields = ["key", "name"]


class CouEventImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CouEventImage
        fields = ["id", "image"]


class CouEventSerializer(serializers.ModelSerializer):
    images = CouEventImageSerializer(many=True, read_only=True)
    types = serializers.SlugRelatedField(
        many=True,
        slug_field="key",
        queryset=CouEventType.objects.all(),
    )
    types_display = serializers.SerializerMethodField()

    class Meta:
        model = CouEvent
        fields = [
            "id",
            "types",
            "types_display",
            "date",
            "location",
            "content",
            "images",
        ]

    def get_types_display(self, obj):
        return [t.name for t in obj.types.all()]


class NewsCoverImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsCoverImage
        fields = ["id", "image"]


class NewsImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsImage
        fields = ["id", "image"]


class NewsSerializer(serializers.ModelSerializer):
    types = serializers.SlugRelatedField(
        many=True,
        slug_field="key",
        queryset=NewsType.objects.all(),
    )
    types_display = serializers.SerializerMethodField()
    cover_image = NewsCoverImageSerializer(many=True, read_only=True)
    images = NewsImageSerializer(many=True, read_only=True)

    class Meta:
        model = News
        fields = [
            "id",
            "date",
            "title",
            "content",
            "types",
            "types_display",
            "cover_image",
            "images",
        ]

    def get_types_display(self, obj):
        return [t.name for t in obj.types.all()]


class NewsTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsType
        fields = ["key", "name"]


class FaqTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FaqType
        fields = ["key", "name"]


class FaqSerializer(serializers.ModelSerializer):
    types = serializers.SlugRelatedField(
        many=True,
        slug_field="key",
        queryset=FaqType.objects.all(),
    )
    types_display = serializers.SerializerMethodField()

    class Meta:
        model = Faq
        fields = [
            "id",
            "question",
            "answer",
            "types",
            "types_display",
        ]

    def get_types_display(self, obj):
        return [t.name for t in obj.types.all()]


class LiteratureTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LiteratureType
        fields = ["key", "name"]


class LiteratureSerializer(serializers.ModelSerializer):
    types = serializers.SlugRelatedField(
        many=True,
        slug_field="key",
        queryset=Literature.objects.all(),
    )
    types_display = serializers.SerializerMethodField()
    published_year = serializers.SerializerMethodField()

    class Meta:
        model = Literature
        fields = [
            "id",
            "title",
            "date",
            "published_year",
            "types",
            "types_display",
            "author",
            "affiliation",
            "link",
        ]

    def get_types_display(self, obj):
        return [t.name for t in obj.types.all()]

    def get_published_year(self, obj):
        return obj.date.year if obj.date else None


class FormLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormLink
        fields = ["id", "title", "link", "file", "created_at"]


class ContactSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Contact
        fields = [
            "id",
            "name",
            "role",
            "university",
            "department",
            "position",
            "mail",
            "image",
            "sort_order",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_image(self, obj):
        if not obj.image:
            return None
        request = self.context.get("request")
        url = obj.image.url
        return request.build_absolute_uri(url) if request else url
