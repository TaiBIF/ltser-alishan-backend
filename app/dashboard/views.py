from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from .models import *
from .serializers import *

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class IntroductionViewSet(viewsets.ModelViewSet):
    queryset = Introduction.objects.all().order_by("id")
    serializer_class = IntroductionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    pagination_class = None

    def get_queryset(self):
        qs = super().get_queryset()
        t = self.request.query_params.get("type")
        if t:
            qs = qs.filter(type=t)
        return qs

    def perform_update(self, serializer):
        instance = self.get_object()
        old_file = instance.media  # 可能是空
        new_file = self.request.FILES.get("media")  # 只有換圖時才有
        instance = serializer.save()
        # 如果有上傳新圖且檔名不同，刪掉舊檔避免堆垃圾
        if new_file and old_file and old_file.name != instance.media.name:
            try:
                old_file.storage.delete(old_file.name)
            except Exception:
                pass


class CouEventFilter(filters.FilterSet):
    content__icontains = filters.CharFilter(
        field_name="content", lookup_expr="icontains"
    )
    location__icontains = filters.CharFilter(
        field_name="location", lookup_expr="icontains"
    )
    date__gte = filters.DateFilter(field_name="date", lookup_expr="gte")
    date__lte = filters.DateFilter(field_name="date", lookup_expr="lte")

    types = filters.CharFilter(method="filter_types")

    class Meta:
        model = CouEvent
        fields = []

    def filter_types(self, queryset, name, value):
        keys = [v.strip() for v in value.split(",") if v.strip()]
        if not keys:
            return queryset
        return queryset.filter(types__key__in=keys).distinct()


class CouEventViewSet(viewsets.ModelViewSet):
    queryset = CouEvent.objects.all().prefetch_related("images").order_by("-date")
    serializer_class = CouEventSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    filter_backends = [DjangoFilterBackend]
    filterset_class = CouEventFilter

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "content__icontains",
                openapi.IN_QUERY,
                description="關鍵字（模糊搜尋）",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "type",
                openapi.IN_QUERY,
                description="活動類型（多個以逗號分隔）",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "location__icontains",
                openapi.IN_QUERY,
                description="地點（模糊搜尋）",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "date__gte",
                openapi.IN_QUERY,
                description="開始日期 YYYY-MM-DD",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "date__lte",
                openapi.IN_QUERY,
                description="結束日期 YYYY-MM-DD",
                type=openapi.TYPE_STRING,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        event = serializer.save()
        # 支援 FormData: append('images', file) 多次；或 append('image', file)
        files = self.request.FILES.getlist("images") or self.request.FILES.getlist(
            "image"
        )
        for f in files:
            CouEventImage.objects.create(event=event, image=f)

    def perform_update(self, serializer):
        event = serializer.save()
        files = self.request.FILES.getlist("images") or self.request.FILES.getlist(
            "image"
        )
        # 預設是「追加新圖」，若要清空再上傳可加一個旗標 clear_images
        clear = self.request.data.get("clear_images")
        if str(clear).lower() in ("1", "true", "yes"):
            event.images.all().delete()
        for f in files:
            CouEventImage.objects.create(event=event, image=f)


class CouEventTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CouEventType.objects.all()
    serializer_class = CouEventTypeSerializer
    pagination_class = None


class NewsFilter(filters.FilterSet):
    title__icontains = filters.CharFilter(field_name="title", lookup_expr="icontains")
    content__icontains = filters.CharFilter(
        field_name="content", lookup_expr="icontains"
    )
    date__gte = filters.DateFilter(field_name="date", lookup_expr="gte")
    date__lte = filters.DateFilter(field_name="date", lookup_expr="lte")

    types = filters.CharFilter(method="filter_types")

    class Meta:
        model = News
        fields = []

    def filter_types(self, queryset, name, value):
        keys = [v.strip() for v in value.split(",") if v.strip()]
        if not keys:
            return queryset
        return queryset.filter(types__key__in=keys).distinct()


class NewsViewSet(viewsets.ModelViewSet):
    queryset = News.objects.all().order_by("-date")
    serializer_class = NewsSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    filter_backends = [DjangoFilterBackend]
    filterset_class = NewsFilter

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "content__icontains",
                openapi.IN_QUERY,
                description="關鍵字（模糊搜尋）",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "types",
                openapi.IN_QUERY,
                description="活動類型（多個以逗號分隔）",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "title__icontains",
                openapi.IN_QUERY,
                description="標題（模糊搜尋）",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "date__gte",
                openapi.IN_QUERY,
                description="開始日期 YYYY-MM-DD",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "date__lte",
                openapi.IN_QUERY,
                description="結束日期 YYYY-MM-DD",
                type=openapi.TYPE_STRING,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class NewsTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = NewsType.objects.all()
    serializer_class = NewsTypeSerializer
    pagination_class = None


class FaqFilter(filters.FilterSet):
    types = filters.CharFilter(method="filter_types")

    class Meta:
        model = Faq
        fields = []

    def filter_types(self, queryset, name, value):
        keys = [v.strip() for v in value.split(",") if v.strip()]
        if not keys:
            return queryset
        return queryset.filter(types__key__in=keys).distinct()


class FaqViewSet(viewsets.ModelViewSet):
    queryset = Faq.objects.all().order_by("id")
    serializer_class = FaqSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    pagination_class = None

    filter_backends = [DjangoFilterBackend]
    filterset_class = FaqFilter

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "types",
                openapi.IN_QUERY,
                description="提問類型（多個以逗號分隔）",
                type=openapi.TYPE_STRING,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class FaqTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FaqType.objects.all()
    serializer_class = FaqTypeSerializer
    pagination_class = None


class LiteratureFilter(filters.FilterSet):
    title__icontains = filters.CharFilter(field_name="title", lookup_expr="icontains")
    author__icontains = filters.CharFilter(field_name="author", lookup_expr="icontains")
    affiliation__icontains = filters.CharFilter(
        field_name="affiliation", lookup_expr="icontains"
    )
    date__gte = filters.DateFilter(field_name="date", lookup_expr="gte")
    date__lte = filters.DateFilter(field_name="date", lookup_expr="lte")

    types = filters.CharFilter(method="filter_types")

    class Meta:
        model = Literature
        fields = []

    def filter_types(self, queryset, name, value):
        keys = [v.strip() for v in value.split(",") if v.strip()]
        if not keys:
            return queryset
        return queryset.filter(types__key__in=keys).distinct()


class LiteratureTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = LiteratureType.objects.all()
    serializer_class = LiteratureTypeSerializer
    pagination_class = None


class LiteratureViewSet(viewsets.ModelViewSet):
    queryset = Literature.objects.all().order_by("id")
    serializer_class = LiteratureSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    filter_backends = [DjangoFilterBackend]
    filterset_class = LiteratureFilter

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "types",
                openapi.IN_QUERY,
                description="文獻類型（多個以逗號分隔）",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "title__icontains",
                openapi.IN_QUERY,
                description="文獻標題",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "author__icontains",
                openapi.IN_QUERY,
                description="作者",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "affiliation__icontains",
                openapi.IN_QUERY,
                description="單位",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "date__gte",
                openapi.IN_QUERY,
                description="開始日期 YYYY-MM-DD",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "date__lte",
                openapi.IN_QUERY,
                description="結束日期 YYYY-MM-DD",
                type=openapi.TYPE_STRING,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class FormLinkViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FormLink.objects.all()
    serializer_class = FormLinkSerializer
    pagination_class = None


class ContactViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    pagination_class = None
