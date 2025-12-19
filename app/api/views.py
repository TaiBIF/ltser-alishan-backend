import os
from collections import defaultdict

from core.base import BaseViewSet
from django.core.cache import cache
from rest_framework.decorators import api_view, permission_classes
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.http import FileResponse, Http404

from django.db.models import Count, Avg, Sum
from django.db.models.functions import TruncDate

from django_filters.rest_framework import DjangoFilterBackend


from .models import *
from .serializers import *
from .filters import *
from .utils.cache_keys import (
    location_map_list_key,
    location_map_filter_key,
    segis_cache_key,
)
from .utils.transform_segis_data import transform_pyramid

from .tasks import generate_download_zip

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .obs_config import OBS_CONFIG


ITEM_PARAM = openapi.Parameter(
    name="item",
    in_=openapi.IN_QUERY,
    description="指定觀測項目（可填中文標籤，例如：植物物候 / 自動照相機監測 ...）",
    type=openapi.TYPE_STRING,
    required=False,
    enum=[cfg["label"] for cfg in OBS_CONFIG.values()],
)


class PlantPhenologyViewSet(BaseViewSet):
    queryset = PlantPhenology.objects.all().order_by("id")
    serializer_class = PlantPhenologySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = PlantPhenologyFilter

    @swagger_auto_schema(query_serializer=PlantPhenologyQuerySerializer)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class PlantPhenologyChartView(APIView):
    @swagger_auto_schema(
        query_serializer=PlantPhenologyChartQuerySerializer,
        responses={
            200: PlantPhenologyChartSerializer(many=True),
            400: openapi.Response(
                description="Bad Request",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"detail": openapi.Schema(type=openapi.TYPE_STRING)},
                ),
            ),
        },
    )
    def get(self, request):
        query_serializer = PlantPhenologyChartQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)
        params = query_serializer.validated_data

        location_id = params["locationID"]
        year = params.get("year")

        qs = PlantPhenology.objects.filter(locationID=location_id)

        if year is not None:
            qs = qs.filter(eventDate__year=year)

        qs = (
            qs.annotate(date=TruncDate("eventDate"))
            .values("date")
            .annotate(species_count=Count("scientificName", distinct=True))
            .order_by("date")
        )

        serializer = PlantPhenologyChartSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CameratrapViewSet(BaseViewSet):
    queryset = Cameratrap.objects.all().order_by("id")
    serializer_class = CameratrapSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = CameratrapFilter

    @swagger_auto_schema(query_serializer=CameratrapQuerySerializer)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class CameratrapChartView(APIView):
    @swagger_auto_schema(
        query_serializer=CameratrapChartQuerySerializer,
        responses={
            200: CameratrapChartSerializer(many=True),
            400: openapi.Response(
                description="Bad Request",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"detail": openapi.Schema(type=openapi.TYPE_STRING)},
                ),
            ),
        },
    )
    def get(self, request):
        query_serializer = CameratrapChartQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)
        params = query_serializer.validated_data

        location_id = params["locationID"]
        year = params.get("year")

        qs = Cameratrap.objects.filter(locationID=location_id)

        if year is not None:
            qs = qs.filter(eventDate__year=year)

        qs = (
            qs.annotate(date=TruncDate("eventDate"))
            .values("date")
            .annotate(species_count=Count("scientificName", distinct=True))
            .order_by("date")
        )

        serializer = CameratrapChartSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TerreSoundIndexViewSet(BaseViewSet):
    queryset = TerreSoundIndex.objects.all().order_by("id")
    serializer_class = TerreSoundIndexSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = TerreSoundIndexFilter

    @swagger_auto_schema(query_serializer=TerreSoundIndexQuerySerializer)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class TerreSoundChartView(APIView):
    @swagger_auto_schema(
        query_serializer=TerreSoundIndexChartQuerySerializer,
        responses={
            200: TerreSoundIndexChartSerializer(many=True),
            400: openapi.Response(
                description="Bad Request",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"detail": openapi.Schema(type=openapi.TYPE_STRING)},
                ),
            ),
        },
    )
    def get(self, request):
        query_serializer = TerreSoundIndexChartQuerySerializer(
            data=request.query_params
        )
        query_serializer.is_valid(raise_exception=True)
        params = query_serializer.validated_data

        location_id = params["locationID"]
        year = params.get("year")

        qs = TerreSoundIndex.objects.filter(locationID=location_id)

        if year is not None:
            qs = qs.filter(measurementDeterminedDate__year=year)

        # 依日期聚合，計算每天平均的 ACI / ADI / BI / NDSI
        qs = (
            qs.annotate(date=TruncDate("measurementDeterminedDate"))
            .values("date")
            .annotate(
                aci=Avg("ACI"),
                adi=Avg("ADI"),
                bi=Avg("BI"),
                ndsi=Avg("NDSI"),
            )
            .order_by("date")
        )

        serializer = TerreSoundIndexChartSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BirdnetSoundViewSet(BaseViewSet):
    queryset = BirdnetSound.objects.all().order_by("id")
    serializer_class = BirdnetSoundSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = BirdnetSoundFilter

    @swagger_auto_schema(query_serializer=BirdnetSoundQuerySerializer)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class BirdnetSoundChartView(APIView):
    @swagger_auto_schema(
        query_serializer=BirdnetSoundChartQuerySerializer,
        responses={
            200: BirdnetSoundChartSerializer(many=True),
            400: openapi.Response(
                description="Bad Request",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"detail": openapi.Schema(type=openapi.TYPE_STRING)},
                ),
            ),
        },
    )
    def get(self, request):
        query_serializer = BirdnetSoundChartQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)
        params = query_serializer.validated_data

        location_id = params["locationID"]
        year = params.get("year")

        qs = BirdnetSound.objects.filter(locationID=location_id)

        if year is not None:
            qs = qs.filter(measurementDeterminedDate__year=year)

        qs = (
            qs.annotate(date=TruncDate("measurementDeterminedDate"))
            .values("date")
            .annotate(species_count=Count("scientificName", distinct=True))
        )

        serializer = BirdnetSoundChartSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BioSoundViewSet(BaseViewSet):
    queryset = BioSound.objects.all().order_by("id")
    serializer_class = BioSoundSerializer
    # filter_backends = [DjangoFilterBackend]
    # filterset_class = BioSoundFilter

    # @swagger_auto_schema(query_serializer=BioSoundQuerySerializer)
    # def list(self, request, *args, **kwargs):
    #     return super().list(request, *args, **kwargs)


class BioSoundChartView(APIView):
    @swagger_auto_schema(
        query_serializer=BioSoundChartQuerySerializer,
        responses={
            200: BioSoundChartSerializer(many=True),
            400: openapi.Response(
                description="Bad Request",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"detail": openapi.Schema(type=openapi.TYPE_STRING)},
                ),
            ),
        },
    )
    def get(self, request):
        query_serializer = BioSoundChartQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)
        params = query_serializer.validated_data

        location_id = params["locationID"]
        year = params.get("year")

        qs = BioSound.objects.filter(locationID=location_id)

        if year is not None:
            qs = qs.filter(measurementDeterminedDate__year=year)

        qs = (
            qs.annotate(date=TruncDate("measurementDeterminedDate"))
            .values("date")
            .annotate(species_count=Count("scientificName", distinct=True))
        )

        serializer = BioSoundChartSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class WeatherViewSet(BaseViewSet):
    queryset = Weather.objects.all().order_by("id")
    serializer_class = WeatherSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = WeatherFilter

    @swagger_auto_schema(query_serializer=WeatherQuerySerializer)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class WeatherChartView(APIView):
    @swagger_auto_schema(
        query_serializer=WeatherChartQuerySerializer,
        responses={
            200: WeatherChartSerializer(many=True),
            400: openapi.Response(
                description="Bad Request",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"detail": openapi.Schema(type=openapi.TYPE_STRING)},
                ),
            ),
        },
    )
    def get(self, request):
        query_serializer = WeatherChartQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)
        params = query_serializer.validated_data

        location_id = params["locationID"]
        year = params.get("year")

        qs = Weather.objects.filter(locationID=location_id)

        if year is not None:
            qs = qs.filter(eventDate__year=year)

        # 依日期聚合，計算每天平均的氣溫 / 每天累積降雨量
        qs = (
            qs.annotate(date=TruncDate("eventDate"))
            .values("date")
            .annotate(
                air_temperature=Avg("AirTemperature"),
                precipitation=Sum("Precipitation"),
            )
            .order_by("date")
        )

        serializer = WeatherChartSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DataFieldViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = BaseDataFieldSerializer
    pagination_class = None

    def get_model_class(self):
        slug = self.request.query_params.get("model")
        if not slug:
            raise ValidationError({"detail": "請提供 ?model=<slug> 參數"})

        cfg = OBS_CONFIG.get(slug)
        # 找不到這個 slug
        if not cfg:
            raise NotFound({"detail": f"未知的 model: {slug}"})

        model = cfg.get("datafield_model")
        if not model:
            # 預防哪一天某個 code 沒設 datafield_model
            raise NotFound({"detail": f"此 model 未設定 datafield_model: {slug}"})

        return model

    def get_queryset(self):
        return self.get_model_class().objects.all().order_by("id")

    def get_serializer_class(self):
        ModelClass = self.get_model_class()

        class DynamicSerializer(BaseDataFieldSerializer):
            class Meta(BaseDataFieldSerializer.Meta):
                model = ModelClass

        return DynamicSerializer

    # enum 直接用 OBS_CONFIG 的 key
    MODEL_PARAM = openapi.Parameter(
        "model",
        openapi.IN_QUERY,
        description="指定要取用的 model（例如 plantphenology / camertrap）",
        type=openapi.TYPE_STRING,
        required=True,
        enum=list(OBS_CONFIG.keys()),
    )

    swagger_decorator = swagger_auto_schema(manual_parameters=[MODEL_PARAM])

    @swagger_decorator
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_decorator
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class LocationViewSet(BaseViewSet):
    queryset = Location.objects.all().order_by("id")
    serializer_class = LocationSerializer
    pagination_class = None
    filter_backends = [DjangoFilterBackend]
    filterset_class = LocationFilter

    @swagger_auto_schema(query_serializer=LocationQuerySerializer)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


YEAR_PARAM = openapi.Parameter(
    "year",
    openapi.IN_QUERY,
    description="指定年份（西元年，例如 2022）",
    type=openapi.TYPE_INTEGER,
    required=False,
)


@swagger_auto_schema(
    method="get",
    operation_description=(
        "依照年份與觀測項目篩選樣站點位。\n"
        "- 不帶參數：回傳所有樣站及其所有年份的觀測項目\n"
        "- 帶 year：只回傳該年有資料的樣站\n"
        "- 帶 year + item：只回傳該年該觀測項目有資料的樣站"
    ),
    manual_parameters=[YEAR_PARAM, ITEM_PARAM],
    responses={200: openapi.Response("成功")},
)
@api_view(["GET"])
def location_map_list(request):
    """
    給首頁觀測地圖畫樣站點位
    """
    OBS_LABEL_TO_CODE = {cfg["label"]: code for code, cfg in OBS_CONFIG.items()}

    year = request.query_params.get("year")
    item = request.query_params.get("item")

    cache_key = location_map_list_key(year, item)
    cached = cache.get(cache_key)
    if cached is not None:
        return Response(cached, status=status.HTTP_200_OK)

    # item 可能是中文，也可能是 code
    item_code = None
    if item:
        # 先當作中文去查，查不到再當作 code 用
        item_code = OBS_LABEL_TO_CODE.get(item, item)

    # 要使用的觀測項目 code 列表
    if item_code:
        # 如果傳來的 code 不在 OBS_CONFIG，就會變成空列表 → 沒資料
        obs_codes = [item_code] if item_code in OBS_CONFIG else []
    else:
        obs_codes = list(OBS_CONFIG.keys())

    locations = Location.objects.order_by("location_id").distinct("location_id")
    result = []

    for loc in locations:
        base = LocationMapSerializer(loc).data
        years_map = defaultdict(list)

        for code in obs_codes:
            cfg = OBS_CONFIG[code]
            model = cfg["model"]
            date_field = cfg["date_field"]

            qs = model.objects.filter(locationID=loc.location_id)

            if year:
                qs = qs.filter(**{f"{date_field}__year": year})

            if year:
                # 只關心這一年：有資料就記錄一次
                if qs.exists():
                    y = int(year)
                    years_map[y].append(cfg["label"])
            else:
                # 沒指定年份 → 把所有有資料的年份列出來
                year_dates = qs.dates(date_field, "year", order="ASC")
                for d in year_dates:
                    y = d.year
                    years_map[y].append(cfg["label"])

        # 如果有帶 year / item，但這個站點完全沒有符合條件的資料 → 跳過
        if year or item:
            if not years_map:
                continue

        base["years"] = {str(y): items for y, items in sorted(years_map.items())}
        result.append(base)

        cache.set(cache_key, result, timeout=None)  # 不過期，等資料更新時再清掉或重算

    return Response(result, status=status.HTTP_200_OK)


@api_view(["GET"])
def location_map_filter(request):
    """
    給首頁觀測地圖年份、觀測項目下拉選單用
    """

    cache_key = location_map_filter_key()
    cached = cache.get(cache_key)
    if cached is not None:
        return Response(cached, status=status.HTTP_200_OK)

    year_map = defaultdict(set)

    for code, cfg in OBS_CONFIG.items():
        model = cfg["model"]
        date_field = cfg["date_field"]

        year_dates = model.objects.dates(date_field, "year", order="ASC")
        for d in year_dates:
            year = d.year
            year_map[year].add(code)

    result = {
        str(year): [OBS_CONFIG[code]["label"] for code in sorted(obs_codes)]
        for year, obs_codes in sorted(year_map.items())
    }

    cache.set(cache_key, result, timeout=None)

    return Response(result, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])  # 如不需要登入可拿掉
def request_download(request):
    """
    建立下載申請，丟給 Celery 背景產 zip 檔並寄信
    前端 body 預期：
    {
        "email": "...",
        "first_name": "...",
        "role": "...",
        "reason": "...",
        "location_id": "XXX",
        "location_name": "某某樣站",
        "year": 2023,
        "items": ["植物物候", "氣象觀測"]  # 或者直接傳 code 也行
    }
    """
    data = request.data

    required_fields = [
        "email",
        "first_name",
        "role",
        "reason",
        "location_id",
        "year",
        "items",
    ]
    for f in required_fields:
        if f not in data:
            return Response(
                {"detail": f"缺少必填欄位：{f}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    try:
        year = int(data["year"])
    except (TypeError, ValueError):
        return Response({"detail": "年份格式錯誤"}, status=status.HTTP_400_BAD_REQUEST)

    items = data.get("items") or []
    if not isinstance(items, list) or not items:
        return Response(
            {"detail": "觀測項目 items 必須為非空陣列"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    dl = DownloadRequest.objects.create(
        email=data["email"],
        first_name=data["first_name"],
        role=data["role"],
        reason=data["reason"],
        location_id=data["location_id"],
        location_name=data.get("location_name", ""),
        year=year,
        items=items,
    )

    # 丟給 celery 背景處理
    generate_download_zip.delay(dl.id)

    return Response(
        {"message": "下載申請已建立", "request_id": dl.id},
        status=status.HTTP_202_ACCEPTED,
    )


@api_view(["GET"])
def download_file(request, pk: int):
    try:
        dl = DownloadRequest.objects.get(pk=pk)
    except DownloadRequest.DoesNotExist:
        raise Http404("下載請求不存在")

    if not dl.zip_path or not os.path.exists(dl.zip_path):
        raise Http404("檔案不存在或已被移除")

    return FileResponse(
        open(dl.zip_path, "rb"),
        as_attachment=True,
        filename=os.path.basename(dl.zip_path),
    )


@api_view(["GET"])
def village_population(request):
    payload = cache.get(segis_cache_key("village_population"))
    if not payload:
        return Response(
            {"detail": "資料尚未建立，請稍後再試"},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
    return Response(payload, status=status.HTTP_200_OK)


@api_view(["GET"])
def village_dynamics(request):
    payload = cache.get(segis_cache_key("village_dynamics"))
    if not payload:
        return Response(
            {"detail": "資料尚未建立，請稍後再試"},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
    return Response(payload, status=status.HTTP_200_OK)


@api_view(["GET"])
def town_pyramid(request):
    rows = cache.get(segis_cache_key("town_pyramid_rows"))
    if not rows:
        return Response(
            {"detail": "資料尚未建立，請稍後再試"},
            status=503,
        )

    year = request.query_params.get("year")
    year = int(year) if year and str(year).isdigit() else None

    payload = transform_pyramid(
        rows,
        selected_year=year,
    )

    return Response(payload, status=200)


@api_view(["GET"])
def town_industry(request):
    payload = cache.get(segis_cache_key("town_industry"))
    if not payload:
        return Response(
            {"detail": "資料尚未建立，請稍後再試"},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
    return Response(payload, status=status.HTTP_200_OK)
