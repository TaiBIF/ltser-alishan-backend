from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Location(models.Model):
    observation_item = models.CharField(max_length=100)
    location_name = models.CharField(max_length=20)
    location_id = models.CharField(max_length=10)
    decimal_longitude = models.DecimalField(
        max_digits=8,
        decimal_places=3,
    )
    decimal_latitude = models.DecimalField(
        max_digits=7,
        decimal_places=3,
    )


class BaseDataField(models.Model):
    field_name = models.CharField(max_length=100)
    field_name_zh_tw = models.CharField(max_length=255)
    field_name_en = models.CharField(max_length=255)
    field_type = models.CharField(max_length=100)
    show_at_filter = models.BooleanField(default=True)
    show_at_table = models.BooleanField(default=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.field_name


class PlantPhenologyDataField(BaseDataField):
    class Meta:
        db_table = "api_plantphenology_data_field"


class CameratrapDataField(BaseDataField):
    class Meta:
        db_table = "api_cameratrap_data_field"


class TerreSoundIndexDataField(BaseDataField):
    class Meta:
        db_table = "api_terresoundindex_data_field"


class BioSoundDataField(BaseDataField):
    class Meta:
        db_table = "api_biosound_data_field"


class BirdnetSoundDataField(BaseDataField):
    class Meta:
        db_table = "api_birdnetsound_data_field"


class WeatherDataField(BaseDataField):
    class Meta:
        db_table = "api_weather_data_field"


class PlantPhenology(models.Model):
    # 1-2 經緯度（可空，但若填一個就必須另一個也填）
    decimalLongitude = models.DecimalField(
        max_digits=13,
        decimal_places=10,
        null=True,
        blank=True,
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
        help_text="地理座標經度（十進位）",
    )
    decimalLatitude = models.DecimalField(
        max_digits=13,
        decimal_places=10,
        null=True,
        blank=True,
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
        help_text="地理座標緯度（十進位）",
    )

    # 3-4 海拔
    minimumElevationInMeters = models.IntegerField(
        null=True, blank=True, help_text="最低海拔(公尺)"
    )
    maximumElevationInMeters = models.IntegerField(
        null=True, blank=True, help_text="最高海拔(公尺)"
    )

    # 5-6 俗名/物種編號
    vernacularName = models.CharField(max_length=255, null=True, blank=True)
    taxonID = models.CharField(max_length=128, null=True, blank=True, db_index=True)

    # 7 中文地點名稱（必填）
    verbatimLocality = models.CharField(max_length=255)

    # 8-9 學名/鑑定層級
    scientificName = models.CharField(
        max_length=255, null=True, blank=True, db_index=True
    )
    taxonRank = models.CharField(max_length=64, null=True, blank=True)

    # 10 英文地點名稱（必填）
    locality = models.CharField(max_length=255)

    # 11 地點代號（必填）
    locationID = models.CharField(max_length=128)

    # 12 事件日期（必填）
    eventDate = models.DateField()

    # 13-14 調查事件ID與資料ID（必填）
    eventID = models.CharField(max_length=255, db_index=True)
    dataID = models.CharField(max_length=255, db_index=True)

    # 15 個體識別碼（可空）
    organismID = models.CharField(max_length=255, null=True, blank=True)

    # 16 調查方法（choices）
    WOODY = "woody"
    HERB = "herb"
    SAMPLING_PROTOCOL_CHOICES = [(WOODY, "woody"), (HERB, "herb")]
    samplingProtocol = models.CharField(
        max_length=16, choices=SAMPLING_PROTOCOL_CHOICES, null=True, blank=True
    )

    # 18-23 葉部百分比（0~100）
    canopyCoverPercentage = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    budCoverPercentage = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    newLeafCoverPercentage = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    matureLeafCoverPercentage = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    yellowLeafCoverPercentage = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    deadLeafCoverPercentage = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    # 24-27 花（總數 + 百分比們）
    totalFlowerCount = models.PositiveIntegerField(null=True, blank=True)
    budFlowerPercentage = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    fullBloomPercentage = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    wiltedFlowerPercentage = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    # 28-32 果（總數 + 百分比們）
    totalFruitCount = models.PositiveIntegerField(null=True, blank=True)
    youngFruitPercentage = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    greenFruitPercentage = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    ripeFruitPercentage = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    wiltedFruitPercentage = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    # 33-39 地表覆蓋/草本高度/各種計數與枯萎比例
    coverInPercentage = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    herbaceousPlantHeight = models.PositiveIntegerField(
        null=True, blank=True, help_text="草本高度(公分)"
    )
    individualCount = models.PositiveIntegerField(null=True, blank=True)
    fruitCount = models.PositiveIntegerField(null=True, blank=True)
    flowerCount = models.PositiveIntegerField(null=True, blank=True)
    budCount = models.PositiveIntegerField(null=True, blank=True)
    wiltedPercentage = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    # 40 動物啃食
    animalGrazing = models.BooleanField(null=True, blank=True)

    # 41-42 樣區大小（數值 + 單位）
    sampleSizeValue = models.FloatField(null=True, blank=True)
    sampleSizeUnit = models.CharField(max_length=64, null=True, blank=True)

    # 時間戳
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "api_plantphenology"
        indexes = [
            models.Index(fields=["eventDate"]),
            models.Index(fields=["locationID"]),
        ]
        verbose_name = "PlantPhenology"
        verbose_name_plural = "PlantPhenology"

    def __str__(self):
        return self.dataID


class Cameratrap(models.Model):
    # 1 觀察類型（必要）
    ANIMAL = "animal"
    HUMAN = "human"
    VEHICLE = "vehicle"
    BLANK = "blank"
    UNKNOWN = "unknown"
    UNCLASSIFIED = "unclassified"
    OBSERVATION_TYPE_CHOICES = [
        (ANIMAL, "animal"),
        (HUMAN, "human"),
        (VEHICLE, "vehicle"),
        (BLANK, "blank"),
        (UNKNOWN, "unknown"),
        (UNCLASSIFIED, "unclassified"),
    ]
    observationType = models.CharField(
        max_length=32,
        choices=OBSERVATION_TYPE_CHOICES,
        help_text="觀察的類型",
    )

    # 2 觀察分級（必要）
    EVENT = "event"
    MEDIA = "media"
    OBSERVATION_LEVEL_CHOICES = [
        (EVENT, "event"),
        (MEDIA, "media"),
    ]
    observationLevel = models.CharField(
        max_length=16,
        choices=OBSERVATION_LEVEL_CHOICES,
        help_text="觀察的分類級別",
    )

    # 3 觀察備註（選填）
    observationComments = models.TextField(
        null=True, blank=True, help_text="有關觀察的評論或備註"
    )

    # 4 設置代號（必要）
    deploymentID = models.CharField(max_length=128, help_text="機器部署的唯一識別碼")

    # 5 時間戳記（必要）
    timestamp = models.DateTimeField(help_text="記錄媒體文件的日期和時間")

    # 6 事件日期（必要）
    eventDate = models.DateField(help_text="事件發生的具體日期", db_index=True)

    # 7 事件時間（必要）
    eventTime = models.TimeField(help_text="事件發生的具體時間")

    # 8 地點註解（選填）
    locationRemarks = models.CharField(
        max_length=255, null=True, blank=True, help_text="關於地點的附註"
    )

    # 9 學名
    scientificName = models.CharField(
        max_length=255, null=True, blank=True, help_text="觀察到的個體的學名"
    )

    # 10 學名作者（選填）
    scientificNameAuthorship = models.CharField(
        max_length=255, null=True, blank=True, help_text="學名的命名者"
    )

    # 11 學名編碼（選填）
    scientificNameID = models.CharField(
        max_length=128,
        null=True,
        blank=True,
        help_text="TaiCOL 學名識別碼",
    )

    # 12 俗名（選填）
    vernacularName = models.CharField(
        max_length=255, null=True, blank=True, help_text="生物的常用名稱"
    )

    # 13 物種編號（選填）
    taxonID = models.CharField(
        max_length=128,
        null=True,
        blank=True,
        help_text="TaiCOL 物種編號",
    )

    # 14 分類階層（選填）
    taxonRank = models.CharField(
        max_length=64, null=True, blank=True, help_text="物種鑑定的最小分類單元"
    )

    # 15 科名（選填）
    family = models.CharField(
        max_length=128, null=True, blank=True, help_text="科的科學名稱"
    )

    # 16 科中文名（選填）
    familyChinese = models.CharField(
        max_length=128, null=True, blank=True, help_text="科中文名"
    )

    # 17 檔案名稱（選填）
    fileName = models.CharField(
        max_length=255, null=True, blank=True, help_text="媒體文件的名稱"
    )

    # 18 檔案路徑（選填；可 URL 或相對路徑）
    filePath = models.CharField(
        max_length=1024, null=True, blank=True, help_text="媒體文件的 URL 或相對路徑"
    )

    # 19 是否公開（必要）
    filePublic = models.BooleanField(default=False, help_text="媒體文件是否可公開訪問")

    # 20 檔案媒體類型（必要，例如 image/jpeg、video/mp4）
    fileMediatype = models.CharField(max_length=64, help_text="媒體文件的媒體類型")

    observationID = models.CharField(max_length=256, help_text="觀察物種的識別碼")

    # 22 性別（選填）
    MALE = "male"
    FEMALE = "female"
    HERMAPHRODITE = "hermaphrodite"
    AMBIGUOUS = "ambiguous"
    SEX_CHOICES = [
        (MALE, "male"),
        (FEMALE, "female"),
        (HERMAPHRODITE, "hermaphrodite"),
        (AMBIGUOUS, "ambiguous"),
    ]
    sex = models.CharField(
        max_length=16,
        choices=SEX_CHOICES,
        null=True,
        blank=True,
        help_text="生物的性別",
    )

    locationID = models.CharField(max_length=128)

    # 時間戳
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "api_cameratrap"
        indexes = [
            models.Index(fields=["eventDate"]),
            models.Index(fields=["locationID"]),
        ]
        verbose_name = "Cameratrap"
        verbose_name_plural = "Cameratrap"

    def __str__(self):
        return self.mediaID


class TerreSoundIndex(models.Model):
    # 1 資料編號（必填）
    dataID = models.CharField(
        max_length=255,
        help_text="每筆資料的辨識碼，以調查事件ID+流水號",
    )

    # 2 事件編號（必填）
    eventID = models.CharField(
        max_length=255,
        help_text="每筆調查事件的辨識碼，以子計畫代碼+調查日期+地點+樣區編號為組成",
    )

    # 3-10 各種聲學指數（數值）
    sh = models.FloatField(
        null=True,
        blank=True,
        help_text="Spectral entropy，量化聲音能量在頻譜上的分散程度",
    )
    th = models.FloatField(
        null=True,
        blank=True,
        help_text="Temporal entropy，量化聲音能量在時間上的分散程度",
    )
    H = models.FloatField(
        null=True,
        blank=True,
        help_text="Acoustic entropy index，描述能量在時間與頻率兩個面向上的分散程度",
    )
    ACI = models.FloatField(
        null=True,
        blank=True,
        help_text="Acoustic complexity index，量化頻率和能量在微細時間的變化",
    )
    ADI = models.FloatField(
        null=True,
        blank=True,
        help_text="Acoustic diversity index，量化聲音內容的多樣性（類似香儂多樣性指數）",
    )
    AEI = models.FloatField(
        null=True,
        blank=True,
        help_text="Acoustic evenness index，聲音均勻度指數（基於吉尼係數）",
    )
    BI = models.FloatField(
        null=True,
        blank=True,
        help_text="Bioacoustic index，用以描述環境中生物聲音的多寡",
    )
    NDSI = models.FloatField(
        null=True,
        blank=True,
        help_text="Normalized Difference Soundscape Index，量化生物聲音與人造聲音相對貢獻量",
    )

    # 11 相關多媒體（錄音檔案名稱或 URL）
    associatedMedia = models.CharField(
        max_length=1024,
        null=True,
        blank=True,
        help_text="相關多媒體，以 URL 為主；在此為錄音檔案名稱",
    )

    # 12-13 錄音長度
    min = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="錄音長度：分鐘數",
    )
    sec = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="錄音長度：秒數",
    )

    # 14 錄音時間（起始時間）
    measurementDeterminedDate = models.DateField(
        help_text="測量項目的量測日期，在此為錄音紀錄起始的時間",
    )

    locationID = models.CharField(max_length=128)
    deploymentID = models.CharField(max_length=128, help_text="機器部署的唯一識別碼")

    # 時間戳
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "api_terresoundindex"
        indexes = [
            models.Index(fields=["measurementDeterminedDate"]),
            models.Index(fields=["locationID"]),
        ]
        verbose_name = "TerreSoundIndex"
        verbose_name_plural = "TerreSoundIndex"

    def __str__(self):
        return self.dataID or self.eventID


class BirdnetSound(models.Model):
    # 1 資料ID（必填，但網頁不顯示）
    dataID = models.CharField(
        max_length=255,
        help_text="每筆資料的辨識碼，以調查事件ID+流水號。",
    )

    # 2 調查事件ID（必填，但網頁不顯示）
    eventID = models.CharField(
        max_length=255,
        help_text="每筆調查事件的辨識碼，以子計畫代碼+調查日期+地點+樣區編號為組成。",
    )

    # 3 俗名（顯示）
    vernacularName = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="物種學名以外的俗名，如中文俗名或英文俗名。",
    )

    # 4 辨識模型版本（BirdNET 模型版本，網頁不顯示）
    model = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="鳥音辨識 BirdNET 模型版本。",
    )

    # 5 起始時間（單位：秒，顯示）
    time_begin = models.FloatField(
        null=True,
        blank=True,
        help_text="鳥音在該錄音檔中的起始時間戳記（秒）。",
    )

    # 6 結束時間（單位：秒，顯示）
    time_end = models.FloatField(
        null=True,
        blank=True,
        help_text="鳥音在該錄音檔中的結束時間戳記（秒）。",
    )

    # 7 信心分數（0–1，顯示）
    confidence = models.FloatField(
        null=True,
        blank=True,
        help_text="模型對該筆辨識結果的置信程度，通常為 0–1 之間的數值。",
    )

    # 8 相關多媒體（錄音檔案名稱或 URL，網頁不顯示文字）
    associatedMedia = models.CharField(
        max_length=1024,
        null=True,
        blank=True,
        help_text="相關多媒體（以 URL 為主），在此為錄音檔案名稱。",
    )

    # 9 錄音時間（起始時間，顯示）
    measurementDeterminedDate = models.DateField(
        null=True,
        blank=True,
        help_text="測量項目的量測日期，在此為錄音紀錄起始的時間。",
    )

    # 10 地點代號（不顯示）
    locationID = models.CharField(
        max_length=128,
        null=True,
        blank=True,
        help_text="地點代號，需參用共用樣站列表。",
    )

    deploymentID = models.CharField(max_length=128, help_text="機器部署的唯一識別碼")

    # 11 物種編號（TaiCOL，顯示）
    taxonID = models.CharField(
        max_length=128,
        null=True,
        blank=True,
        help_text="由 TaiCOL 網站所定義的物種編號。",
    )

    # 12 物種學名（必填，顯示）
    scientificName = models.CharField(
        max_length=255,
        help_text="調查物種的拉丁學名，為鑑定至最低階層的完整學名。",
    )

    # 13 物種鑑定層級（網頁不顯示）
    taxonRank = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        help_text="調查物種所列學名的鑑定層級。",
    )

    # 14 學名編碼（TaiCOL，數字，網頁不顯示）
    scientificNameID = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="由 TaiCOL 所賦予的學名的唯一識別碼。",
    )

    # 15 科名（網頁不顯示）
    family = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="生物分類單元「科」之科學名稱。",
    )

    # 16 科中文名（網頁不顯示）
    familyChinese = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="科中文名。",
    )

    # # 17 模型使用的學名（BirdNET 2.4，網頁不顯示）
    # birdnet2_4 = models.CharField(
    #     max_length=255,
    #     null=True,
    #     blank=True,
    #     help_text="由 BirdNET 2.4 模型辨識出的物種學名。",
    # )

    # # 18 模型使用的英文俗名（網頁不顯示）
    # unsafe_2023_tw___ = models.CharField(
    #     "模型使用的英文俗名",
    #     max_length=255,
    #     null=True,
    #     blank=True,
    #     help_text="由 BirdNET 2.4 模型輸出結果所對應的英文俗名。",
    # )

    # # 19 模型使用的中文俗名（網頁不顯示）
    # unsafe_2023_tw____2 = models.CharField(
    #     "模型使用的中文俗名",
    #     max_length=255,
    #     null=True,
    #     blank=True,
    #     help_text="由 BirdNET 2.4 模型輸出結果所對應的中文俗名。",
    # )

    # 時間戳
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "api_birdnetsound"
        indexes = [
            models.Index(fields=["measurementDeterminedDate"]),
            models.Index(fields=["locationID"]),
        ]
        verbose_name = "BirdnetSound"
        verbose_name_plural = "BirdnetSound"

    def __str__(self):
        return self.dataID


class BioSound(models.Model):
    # 1 資料ID（必填，但網頁不顯示）
    dataID = models.CharField(
        max_length=255,
        help_text="每筆資料的辨識碼，以調查事件ID+流水號。",
    )

    # 2 調查事件ID（必填，但網頁不顯示）
    eventID = models.CharField(
        max_length=255,
        help_text="每筆調查事件的辨識碼，以子計畫代碼+調查日期+地點+樣區編號為組成。",
    )

    # 3 SILIC 物種ID（顯示）
    classid = models.IntegerField(
        null=True,
        blank=True,
        help_text="SILIC 物種ID。",
    )

    # 4 物種學名（必填，顯示）
    scientificName = models.CharField(
        max_length=255,
        help_text="調查物種的拉丁學名，為鑑定至最低階層的完整學名。",
    )

    # 5 物種鑑定層級（必填，網頁不顯示）
    taxonRank = models.CharField(
        max_length=64,
        help_text="調查物種所列學名的鑑定層級。",
    )

    # 6 俗名（顯示）
    vernacularName = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="物種學名以外的俗名，如中文俗名或英文俗名。",
    )

    # 7 叫聲類型（顯示）
    soundclass = models.CharField(
        max_length=16,
        null=True,
        blank=True,
        help_text="叫聲類型，如：鳴唱或鳴叫聲分別以 S 或 C 表示。",
    )

    # 8 起始時間（毫秒，顯示）
    time_begin = models.FloatField(
        null=True,
        blank=True,
        help_text="鳥音在該錄音檔中的起始時間戳記（毫秒）。",
    )

    # 9 結束時間（毫秒，顯示）
    time_end = models.FloatField(
        null=True,
        blank=True,
        help_text="鳥音在該錄音檔中的結束時間戳記（毫秒）。",
    )

    # 10 信心分數（0–1，顯示）
    confidence = models.FloatField(
        null=True,
        blank=True,
        help_text="模型對該筆辨識結果的置信程度，通常為 0–1 之間的數值。",
    )

    # 11 相關多媒體（錄音檔案名稱或 URL，網頁不顯示文字）
    associatedMedia = models.CharField(
        max_length=1024,
        null=True,
        blank=True,
        help_text="相關多媒體（以 URL 為主），在此為錄音檔案名稱。",
    )

    # 12 聲紋最低頻率（Hz，顯示）
    freq_low = models.FloatField(
        null=True,
        blank=True,
        help_text="鳥音聲紋之最低頻率（Hz）。",
    )

    # 13 聲紋最高頻率（Hz，顯示）
    freq_high = models.FloatField(
        null=True,
        blank=True,
        help_text="鳥音聲紋之最高頻率（Hz）。",
    )

    # 14 錄音時間（起始時間，必填，顯示）
    measurementDeterminedDate = models.DateField(
        help_text="測量項目的量測日期，在此為錄音紀錄起始的時間。",
    )

    # 15 地點代號（必填，不顯示）
    locationID = models.CharField(
        max_length=128,
        help_text="地點代號，需參用共用樣站列表。",
    )

    # 時間戳
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "api_biosound"
        indexes = [
            models.Index(fields=["measurementDeterminedDate"]),
            models.Index(fields=["locationID"]),
        ]
        verbose_name = "BioSound"
        verbose_name_plural = "BioSound"

    def __str__(self):
        return self.dataID


class Weather(models.Model):

    # 1 資料編號（必填）
    dataID = models.CharField(
        max_length=255,
        help_text="每筆資料的辨識碼，由事件編號加上流水號（以 '-' 連接）。",
    )

    # 2 事件編號（必填）
    eventID = models.CharField(
        max_length=255,
        help_text="每筆事件的辨識碼，由子計畫代碼、調查日期、部署代碼組成（以 '-' 連接）。",
    )

    # 3 地點編號（必填）
    locationID = models.CharField(
        max_length=128,
        help_text="地點代號，需參照共用樣站列表以保持一致性。",
    )

    # 4 部署編號（必填）
    deploymentID = models.CharField(
        max_length=255,
        help_text="機器部署的唯一識別碼，用於追蹤不同部署設備。",
    )

    # 5 事件日期（ISO 8601, YYYY-MM-DD）
    eventDate = models.DateField(
        help_text="觀測事件發生的日期（ISO 8601：YYYY-MM-DD）。",
    )

    # 6 事件時間（ISO 8601 時間格式）
    eventTime = models.CharField(
        max_length=20,
        help_text="觀測事件發生的時間（ISO 8601，格式如 hh:mm:ssZ 或 hh:mm:ss±hh:mm）。",
    )

    # 7 PAR
    PAR = models.FloatField(
        # validators=[MinValueValidator(0), MaxValueValidator(4000)],
        null=True,
        blank=True,
        help_text="光合作用有效輻射 PPFD（400–700 nm），單位 µmol/m²/s，範圍 0–4000。",
    )

    # 8 葉面濕潤指數（選填）
    WetnessLevel = models.FloatField(
        null=True,
        blank=True,
        help_text="葉片表面濕潤程度之原始感測數值，數值越高表示越濕。",
    )

    # 9 氣溫 °C
    AirTemperature = models.FloatField(
        # validators=[MinValueValidator(-40.0), MaxValueValidator(80.0)],
        null=True,
        blank=True,
        help_text="氣溫（°C），範圍 -40.0 ~ 80.0。",
    )

    # 10 相對濕度 %（
    RelativeHumidity = models.FloatField(
        # validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        null=True,
        blank=True,
        help_text="相對溼度（%），範圍 0.0 ~ 100.0。",
    )

    # 11 氣壓（hPa）
    AirPressure = models.FloatField(
        # validators=[MinValueValidator(10.0), MaxValueValidator(1200.0)],
        null=True,
        blank=True,
        help_text="大氣壓力（hPa），範圍 10.0 ~ 1200.0。",
    )

    # 12 土壤體積含水量（選填）
    WaterContent = models.FloatField(
        null=True,
        blank=True,
        # validators=[MinValueValidator(0.00), MaxValueValidator(0.70)],
        help_text="土壤體積含水量（0.00 = 全乾，1.00 = 完全飽和），範圍 0.00 ~ 0.70。",
    )

    # 13 地溫 °C（選填）
    SoilTemperature = models.FloatField(
        null=True,
        blank=True,
        # validators=[MinValueValidator(-40.0), MaxValueValidator(60.0)],
        help_text="土壤溫度（°C），範圍 -40.0 ~ 60.0。",
    )

    # 14 風向（度）（選填）
    WindDirection = models.FloatField(
        null=True,
        blank=True,
        # validators=[MinValueValidator(0.0), MaxValueValidator(359.0)],
        help_text="風向（度），0°=北、90°=東、180°=南、270°=西。",
    )

    # 15 風速（m/s）（選填）
    WindSpeed = models.FloatField(
        null=True,
        blank=True,
        # validators=[MinValueValidator(0.0), MaxValueValidator(30.0)],
        help_text="風速（m/s），範圍 0.0 ~ 30.0。",
    )

    # 16 瞬間風速（m/s）（選填）
    GustSpeed = models.FloatField(
        null=True,
        blank=True,
        # validators=[MinValueValidator(0.0), MaxValueValidator(30.0)],
        help_text="瞬間風速（m/s），範圍 0.0 ~ 30.0。",
    )

    # 17 降水量（mm）（選填）
    Precipitation = models.FloatField(
        null=True,
        blank=True,
        # validators=[MinValueValidator(0.0), MaxValueValidator(9999.9)],
        help_text="降水量（mm），範圍 0.0 ~ 9999.9。",
    )

    # 系統時間戳
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "api_weather"
        indexes = [
            models.Index(fields=["eventDate"]),
            models.Index(fields=["locationID"]),
        ]
        verbose_name = "Weather"
        verbose_name_plural = "Weather"

    def __str__(self):
        return self.dataID


class DownloadRequest(models.Model):
    STATUS_PENDING = "pending"
    STATUS_PROCESSING = "processing"
    STATUS_DONE = "done"
    STATUS_FAILED = "failed"
    STATUS_EXPIRED = "expired"

    STATUS_CHOICES = [
        (STATUS_PENDING, "待處理"),
        (STATUS_PROCESSING, "處理中"),
        (STATUS_DONE, "已完成"),
        (STATUS_FAILED, "失敗"),
        (STATUS_EXPIRED, "已過期"),
    ]

    email = models.EmailField()
    first_name = models.CharField(max_length=100, blank=True)
    role = models.CharField(max_length=100, blank=True)
    reason = models.TextField(blank=True)

    # 從前端帶來的條件
    location_id = models.CharField(max_length=100)
    location_name = models.CharField(max_length=255, blank=True)
    year = models.IntegerField()
    items = models.JSONField(default=list)

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    zip_path = models.CharField(max_length=500, blank=True)
    error_message = models.TextField(blank=True)

    email_sent = models.BooleanField(default=False)
    email_error = models.TextField(blank=True)

    class Meta:
        db_table = "api_download_request"
        verbose_name = "DownloadRequest"
        verbose_name_plural = "DownloadRequests"

    def __str__(self):
        return f"{self.email} - {self.location_id} - {self.year}"
