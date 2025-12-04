from rest_framework import serializers
from .models import *


class PlantPhenologySerializer(serializers.ModelSerializer):
    class Meta:
        model = PlantPhenology
        fields = "__all__"


# 定義 Swagger 上顯示的欄位 & 驗證 query 參數
class PlantPhenologyQuerySerializer(serializers.Serializer):
    decimalLongitude = serializers.FloatField(
        required=False, help_text="經度（十進位）"
    )
    decimalLatitude = serializers.FloatField(required=False, help_text="緯度（十進位）")
    minimumElevationInMeters = serializers.FloatField(
        required=False, help_text="最低海拔"
    )
    maximumElevationInMeters = serializers.FloatField(
        required=False, help_text="最高海拔"
    )
    vernacularName = serializers.CharField(required=False, help_text="俗名")
    taxonID = serializers.CharField(required=False, help_text="物種編號")
    verbatimLocality = serializers.CharField(required=False, help_text="中文地點名稱")
    scientificName = serializers.CharField(required=False, help_text="物種學名")
    taxonRank = serializers.CharField(required=False, help_text="物種鑑定層級")
    locality = serializers.CharField(required=False, help_text="地點名稱")
    locationID = serializers.CharField(required=False, help_text="地點代號")
    eventStartDate = serializers.DateField(
        required=False, help_text="事件起始日期（因搜尋功能而衍生的欄位）"
    )
    eventEndDate = serializers.DateField(
        required=False, help_text="事件結束日期（因搜尋功能而衍生的欄位）"
    )
    eventID = serializers.CharField(required=False, help_text="調查事件ID")
    dataID = serializers.CharField(required=False, help_text="資料ID")
    organismID = serializers.CharField(required=False, help_text="個體的識別碼")
    samplingProtocol = serializers.CharField(required=False, help_text="調查方法")
    recordedBy = serializers.CharField(required=False, help_text="紀錄者/觀察者")
    canopyCoverPercentage = serializers.FloatField(required=False, help_text="葉")
    budCoverPercentage = serializers.FloatField(required=False, help_text="葉芽")
    newLeafCoverPercentage = serializers.FloatField(required=False, help_text="新葉")
    matureLeafCoverPercentage = serializers.FloatField(
        required=False, help_text="成熟葉"
    )
    yellowLeafCoverPercentage = serializers.FloatField(required=False, help_text="黃葉")
    deadLeafCoverPercentage = serializers.FloatField(required=False, help_text="枯葉")
    totalFlowerCount = serializers.FloatField(required=False, help_text="花（數量）")
    budFlowerPercentage = serializers.FloatField(required=False, help_text="花苞")
    fullBloomPercentage = serializers.FloatField(required=False, help_text="盛開")
    wiltedFlowerPercentage = serializers.FloatField(required=False, help_text="枯萎")
    totalFruitCount = serializers.FloatField(required=False, help_text="果（數量）")
    youngFruitPercentage = serializers.FloatField(required=False, help_text="幼果")
    greenFruitPercentage = serializers.FloatField(required=False, help_text="綠果")
    ripeFruitPercentage = serializers.FloatField(required=False, help_text="熟果")
    wiltedFruitPercentage = serializers.FloatField(required=False, help_text="覆蓋度")
    coverInPercentage = serializers.FloatField(required=False, help_text="枯萎果")
    herbaceousPlantHeight = serializers.FloatField(required=False, help_text="草本高度")
    individualCount = serializers.FloatField(required=False, help_text="數量")
    fruitCount = serializers.FloatField(required=False, help_text="果實數")
    flowerCount = serializers.FloatField(required=False, help_text="開花數")
    budCount = serializers.FloatField(required=False, help_text="出芽數")
    wiltedPercentage = serializers.FloatField(required=False, help_text="枯萎度")
    animalGrazing = serializers.BooleanField(required=False, help_text="動物啃食")
    sampleSizeValue = serializers.FloatField(required=False, help_text="樣區大小數值")
    sampleSizeUnit = serializers.CharField(required=False, help_text="樣區單位")


class PlantPhenologyChartSerializer(serializers.Serializer):
    date = serializers.DateField()
    species_count = serializers.IntegerField()


class PlantPhenologyChartQuerySerializer(serializers.Serializer):
    locationID = serializers.CharField(required=True, help_text="指定地點代號")
    year = serializers.IntegerField(required=False, help_text="指定年份（西元年）")


class CameratrapSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cameratrap
        fields = "__all__"


class CameratrapQuerySerializer(serializers.Serializer):
    observationType = serializers.CharField(
        required=False,
        help_text="觀察的類型",
    )
    observationLevel = serializers.CharField(
        required=False,
        help_text="觀察的分類級別",
    )
    observationComments = serializers.CharField(
        required=False,
        help_text="有關觀察的評論或備註",
    )
    deploymentID = serializers.CharField(
        required=False,
        help_text="機器部署的唯一識別碼",
    )
    eventStartDate = serializers.DateField(
        required=False,
        help_text="事件起始日期（因搜尋功能而衍生的欄位）",
    )
    eventEndDate = serializers.DateField(
        required=False,
        help_text="事件結束日期（因搜尋功能而衍生的欄位）",
    )
    locationRemarks = serializers.CharField(
        required=False,
        help_text="關於地點的附註",
    )
    scientificName = serializers.CharField(
        required=False,
        help_text="觀察到的個體的學名",
    )
    scientificNameAuthorship = serializers.CharField(
        required=False,
        help_text="學名的命名者",
    )
    scientificNameID = serializers.CharField(
        required=False,
        help_text="TaiCOL 學名識別碼",
    )
    vernacularName = serializers.CharField(
        required=False,
        help_text="生物的常用名稱",
    )
    taxonID = serializers.CharField(
        required=False,
        help_text="TaiCOL 物種編號",
    )
    taxonRank = serializers.CharField(
        required=False,
        help_text="物種鑑定的最小分類單元",
    )
    family = serializers.CharField(
        required=False,
        help_text="科的科學名稱",
    )
    familyChinese = serializers.CharField(
        required=False,
        help_text="科中文名",
    )
    fileName = serializers.CharField(
        required=False,
        help_text="媒體文件的名稱",
    )
    filePath = serializers.CharField(
        required=False,
        help_text="媒體文件的 URL 或相對路徑",
    )
    filePublic = serializers.BooleanField(
        required=False,
        help_text="媒體文件是否可公開訪問",
    )
    fileMediatype = serializers.CharField(
        required=False,
        help_text="媒體文件的媒體類型",
    )
    observationID = serializers.CharField(
        required=False,
        help_text="觀察物種的識別碼",
    )
    sex = serializers.CharField(
        required=False,
        help_text="生物的性別",
    )
    locationID = serializers.CharField(
        required=False,
        help_text="地點代號",
    )


class CameratrapChartSerializer(serializers.Serializer):
    date = serializers.DateField()
    species_count = serializers.IntegerField()


class CameratrapChartQuerySerializer(serializers.Serializer):
    locationID = serializers.CharField(required=True, help_text="指定地點代號")
    year = serializers.IntegerField(required=False, help_text="指定年份（西元年）")


class TerreSoundIndexSerializer(serializers.ModelSerializer):
    class Meta:
        model = TerreSoundIndex
        fields = "__all__"


class TerreSoundIndexQuerySerializer(serializers.Serializer):
    dataID = serializers.CharField(
        required=False,
        help_text="每筆資料的辨識碼，以調查事件ID+流水號",
    )
    eventID = serializers.CharField(
        required=False,
        help_text="每筆調查事件的辨識碼，以子計畫代碼+調查日期+地點+樣區編號為組成",
    )
    sh = serializers.FloatField(
        required=False,
        help_text="Spectral entropy，量化聲音能量在頻譜上的分散程度",
    )
    th = serializers.FloatField(
        required=False,
        help_text="Temporal entropy，量化聲音能量在時間上的分散程度",
    )
    H = serializers.FloatField(
        required=False,
        help_text="Acoustic entropy index，描述能量在時間與頻率兩個面向上的分散程度",
    )
    ACI = serializers.FloatField(
        required=False,
        help_text="Acoustic complexity index，量化頻率和能量在微細時間的變化",
    )
    ADI = serializers.FloatField(
        required=False,
        help_text="Acoustic diversity index，量化聲音內容的多樣性（類似香儂多樣性指數）",
    )
    AEI = serializers.FloatField(
        required=False,
        help_text="Acoustic evenness index，聲音均勻度指數（基於吉尼係數）",
    )
    BI = serializers.FloatField(
        required=False,
        help_text="Bioacoustic index，用以描述環境中生物聲音的多寡",
    )
    NDSI = serializers.FloatField(
        required=False,
        help_text="Normalized Difference Soundscape Index，量化生物聲音與人造聲音相對貢獻量",
    )
    associatedMedia = serializers.CharField(
        required=False,
        help_text="相關多媒體，以 URL 為主；在此為錄音檔案名稱",
    )
    measurementStartDate = serializers.DateField(
        required=False,
        help_text="量測日期起始（因搜尋功能而衍生的欄位）",
    )
    measurementEndDate = serializers.DateField(
        required=False,
        help_text="量測日期結束（因搜尋功能而衍生的欄位）",
    )
    locationID = serializers.CharField(
        required=False,
        help_text="地點代號",
    )
    deploymentID = serializers.CharField(
        required=False,
        help_text="機器部署的唯一識別碼",
    )


class TerreSoundIndexChartSerializer(serializers.Serializer):
    date = serializers.DateField()
    aci = serializers.FloatField()
    adi = serializers.FloatField()
    bi = serializers.FloatField()
    ndsi = serializers.FloatField()


class TerreSoundIndexChartQuerySerializer(serializers.Serializer):
    locationID = serializers.CharField(required=True, help_text="指定地點代號")
    year = serializers.IntegerField(required=False, help_text="指定年份（西元年）")


class BirdnetSoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = BirdnetSound
        fields = "__all__"


class BirdnetSoundQuerySerializer(serializers.Serializer):
    dataID = serializers.CharField(
        required=False,
        help_text="每筆資料的辨識碼，以調查事件ID+流水號。",
    )
    eventID = serializers.CharField(
        required=False,
        help_text="每筆調查事件的辨識碼，以子計畫代碼+調查日期+地點+樣區編號為組成。",
    )
    vernacularName = serializers.CharField(
        required=False,
        help_text="物種學名以外的俗名，如中文俗名或英文俗名。",
    )
    model = serializers.CharField(
        required=False,
        help_text="鳥音辨識 BirdNET 模型版本。",
    )
    time_begin = serializers.FloatField(
        required=False,
        help_text="鳥音在該錄音檔中的起始時間戳記（秒）。",
    )
    time_end = serializers.FloatField(
        required=False,
        help_text="鳥音在該錄音檔中的結束時間戳記（秒）。",
    )
    confidence = serializers.FloatField(
        required=False,
        help_text="模型對該筆辨識結果的置信程度，通常為 0–1 之間的數值。",
    )
    associatedMedia = serializers.CharField(
        required=False,
        help_text="相關多媒體（以 URL 為主），在此為錄音檔案名稱。",
    )
    measurementStartDate = serializers.DateField(
        required=False,
        help_text="量測日期起始（因搜尋功能而衍生的欄位）。",
    )
    measurementEndDate = serializers.DateField(
        required=False,
        help_text="量測日期結束（因搜尋功能而衍生的欄位）。",
    )
    locationID = serializers.CharField(
        required=False,
        help_text="地點代號，需參用共用樣站列表。",
    )
    deploymentID = serializers.CharField(
        required=False,
        help_text="機器部署的唯一識別碼",
    )
    taxonID = serializers.CharField(
        required=False,
        help_text="由 TaiCOL 網站所定義的物種編號。",
    )
    scientificName = serializers.CharField(
        required=False,
        help_text="調查物種的拉丁學名，為鑑定至最低階層的完整學名。",
    )
    taxonRank = serializers.CharField(
        required=False,
        help_text="調查物種所列學名的鑑定層級。",
    )
    scientificNameID = serializers.IntegerField(
        required=False,
        help_text="由 TaiCOL 所賦予的學名的唯一識別碼。",
    )
    family = serializers.CharField(
        required=False,
        help_text="生物分類單元「科」之科學名稱。",
    )
    familyChinese = serializers.CharField(
        required=False,
        help_text="科中文名。",
    )


class BirdnetSoundChartSerializer(serializers.Serializer):
    date = serializers.DateField()
    species_count = serializers.IntegerField()


class BirdnetSoundChartQuerySerializer(serializers.Serializer):
    locationID = serializers.CharField(required=True, help_text="指定地點代號")
    year = serializers.IntegerField(required=False, help_text="指定年份（西元年）")


class BioSoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = BioSound
        fields = "__all__"


class BioSoundChartSerializer(serializers.Serializer):
    date = serializers.DateField()
    species_count = serializers.IntegerField()


class BioSoundChartQuerySerializer(serializers.Serializer):
    locationID = serializers.CharField(required=True, help_text="指定地點代號")
    year = serializers.IntegerField(required=False, help_text="指定年份（西元年）")


class WeatherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Weather
        fields = "__all__"


class WeatherQuerySerializer(serializers.Serializer):
    dataID = serializers.CharField(
        required=False,
        help_text="每筆資料的辨識碼，由事件編號加上流水號（以 '-' 連接）。",
    )
    eventID = serializers.CharField(
        required=False,
        help_text="每筆事件的辨識碼，由子計畫代碼、調查日期、部署代碼組成（以 '-' 連接）。",
    )
    locationID = serializers.CharField(
        required=False,
        help_text="地點代號，需參照共用樣站列表以保持一致性。",
    )
    deploymentID = serializers.CharField(
        required=False,
        help_text="機器部署的唯一識別碼，用於追蹤不同部署設備。",
    )
    eventDate = serializers.DateField(
        required=False,
        help_text="觀測事件發生的日期（ISO 8601：YYYY-MM-DD）。",
    )
    eventStartDate = serializers.DateField(
        required=False,
        help_text="觀測事件日期起始（搜尋用欄位，對應 eventDate，條件為大於等於）。",
    )
    eventEndDate = serializers.DateField(
        required=False,
        help_text="觀測事件日期結束（搜尋用欄位，對應 eventDate，條件為小於等於）。",
    )
    eventTime = serializers.CharField(
        required=False,
        help_text="觀測事件發生的時間（ISO 8601，格式如 hh:mm:ssZ 或 hh:mm:ss±hh:mm）。",
    )

    PAR = serializers.FloatField(
        required=False,
        help_text="光合作用有效輻射 PPFD（400–700 nm），單位 µmol/m²/s，範圍 0–4000。",
    )
    WetnessLevel = serializers.FloatField(
        required=False,
        help_text="葉片表面濕潤程度之原始感測數值，數值越高表示越濕。",
    )
    AirTemperature = serializers.FloatField(
        required=False,
        help_text="氣溫（°C），範圍 -40.0 ~ 80.0。",
    )
    RelativeHumidity = serializers.FloatField(
        required=False,
        help_text="相對溼度（%），範圍 0.0 ~ 100.0。",
    )
    AirPressure = serializers.FloatField(
        required=False,
        help_text="大氣壓力（hPa），範圍 10.0 ~ 1200.0。",
    )
    WaterContent = serializers.FloatField(
        required=False,
        help_text="土壤體積含水量（0.00 = 全乾，1.00 = 完全飽和），範圍 0.00 ~ 0.70。",
    )
    SoilTemperature = serializers.FloatField(
        required=False,
        help_text="土壤溫度（°C），範圍 -40.0 ~ 60.0。",
    )
    WindDirection = serializers.FloatField(
        required=False,
        help_text="風向（度），0°=北、90°=東、180°=南、270°=西。",
    )
    WindSpeed = serializers.FloatField(
        required=False,
        help_text="風速（m/s），範圍 0.0 ~ 30.0。",
    )
    GustSpeed = serializers.FloatField(
        required=False,
        help_text="瞬間風速（m/s），範圍 0.0 ~ 30.0。",
    )
    Precipitation = serializers.FloatField(
        required=False,
        help_text="降水量（mm），範圍 0.0 ~ 9999.9。",
    )


class WeatherChartSerializer(serializers.Serializer):
    date = serializers.DateField()
    air_temperature = serializers.FloatField()
    precipitation = serializers.FloatField()


class WeatherChartQuerySerializer(serializers.Serializer):
    locationID = serializers.CharField(required=True, help_text="指定地點代號")
    year = serializers.IntegerField(required=False, help_text="指定年份（西元年）")


class BaseDataFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseDataField
        fields = "__all__"


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = "__all__"


class LocationQuerySerializer(serializers.Serializer):
    observation_item = serializers.CharField(required=False, help_text="觀測項目")


class LocationMapSerializer(serializers.ModelSerializer):
    decimal_longitude = serializers.FloatField()
    decimal_latitude = serializers.FloatField()
    position = serializers.SerializerMethodField()

    class Meta:
        model = Location
        fields = (
            "location_id",
            "location_name",
            "decimal_longitude",
            "decimal_latitude",
            "position",
        )

    def get_position(self, obj):
        return [float(obj.decimal_latitude), float(obj.decimal_longitude)]
