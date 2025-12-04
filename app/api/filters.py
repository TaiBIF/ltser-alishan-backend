from django_filters.rest_framework import (
    FilterSet,
    CharFilter,
    DateFilter,
    NumberFilter,
    BooleanFilter,
)
from .models import *


class LocationFilter(FilterSet):
    observation_item = CharFilter(field_name="observation_item", lookup_expr="exact")

    class Meta:
        model = Location
        fields = []


# 定義後端真正的查詢邏輯
class PlantPhenologyFilter(FilterSet):
    decimalLongitude = NumberFilter(field_name="decimalLongitude", lookup_expr="exact")
    decimalLatitude = NumberFilter(field_name="decimalLatitude", lookup_expr="exact")
    minimumElevationInMeters = NumberFilter(
        field_name="minimumElevationInMeters", lookup_expr="exact"
    )
    maximumElevationInMeters = NumberFilter(
        field_name="maximumElevationInMeters", lookup_expr="exact"
    )
    vernacularName = CharFilter(field_name="vernacularName", lookup_expr="exact")
    taxonID = CharFilter(field_name="taxonID", lookup_expr="exact")
    verbatimLocality = CharFilter(field_name="verbatimLocality", lookup_expr="exact")
    scientificName = CharFilter(field_name="scientificName", lookup_expr="exact")
    taxonRank = CharFilter(field_name="taxonRank", lookup_expr="exact")
    locality = CharFilter(field_name="locality", lookup_expr="exact")
    locationID = CharFilter(field_name="locationID", lookup_expr="exact")
    eventStartDate = DateFilter(field_name="eventDate", lookup_expr="gte")
    eventEndDate = DateFilter(field_name="eventDate", lookup_expr="lte")
    eventID = CharFilter(field_name="eventID", lookup_expr="exact")
    dataID = CharFilter(field_name="dataID", lookup_expr="exact")
    organismID = CharFilter(field_name="organismID", lookup_expr="exact")
    samplingProtocol = CharFilter(field_name="samplingProtocol", lookup_expr="exact")
    recordedBy = CharFilter(field_name="recordedBy", lookup_expr="exact")
    canopyCoverPercentage = NumberFilter(
        field_name="canopyCoverPercentage", lookup_expr="exact"
    )
    budCoverPercentage = NumberFilter(
        field_name="budCoverPercentage", lookup_expr="exact"
    )
    newLeafCoverPercentage = NumberFilter(
        field_name="newLeafCoverPercentage", lookup_expr="exact"
    )
    matureLeafCoverPercentage = NumberFilter(
        field_name="matureLeafCoverPercentage", lookup_expr="exact"
    )
    yellowLeafCoverPercentage = NumberFilter(
        field_name="yellowLeafCoverPercentage", lookup_expr="exact"
    )
    deadLeafCoverPercentage = NumberFilter(
        field_name="deadLeafCoverPercentage", lookup_expr="exact"
    )
    totalFlowerCount = NumberFilter(field_name="totalFlowerCount", lookup_expr="exact")
    budFlowerPercentage = NumberFilter(
        field_name="budFlowerPercentage", lookup_expr="exact"
    )
    fullBloomPercentage = NumberFilter(
        field_name="fullBloomPercentage", lookup_expr="exact"
    )
    wiltedFlowerPercentage = NumberFilter(
        field_name="wiltedFlowerPercentage", lookup_expr="exact"
    )
    totalFruitCount = NumberFilter(field_name="totalFruitCount", lookup_expr="exact")
    youngFruitPercentage = NumberFilter(
        field_name="youngFruitPercentage", lookup_expr="exact"
    )
    greenFruitPercentage = NumberFilter(
        field_name="greenFruitPercentage", lookup_expr="exact"
    )
    ripeFruitPercentage = NumberFilter(
        field_name="ripeFruitPercentage", lookup_expr="exact"
    )
    wiltedFruitPercentage = NumberFilter(
        field_name="wiltedFruitPercentage", lookup_expr="exact"
    )
    coverInPercentage = NumberFilter(
        field_name="coverInPercentage", lookup_expr="exact"
    )
    herbaceousPlantHeight = NumberFilter(
        field_name="herbaceousPlantHeight", lookup_expr="exact"
    )
    individualCount = NumberFilter(field_name="individualCount", lookup_expr="exact")
    fruitCount = NumberFilter(field_name="fruitCount", lookup_expr="exact")
    flowerCount = NumberFilter(field_name="flowerCount", lookup_expr="exact")
    budCount = NumberFilter(field_name="budCount", lookup_expr="exact")
    wiltedPercentage = NumberFilter(field_name="wiltedPercentage", lookup_expr="exact")
    animalGrazing = BooleanFilter(field_name="animalGrazing", lookup_expr="exact")
    sampleSizeValue = NumberFilter(field_name="sampleSizeValue", lookup_expr="exact")
    sampleSizeUnit = CharFilter(field_name="sampleSizeUnit", lookup_expr="exact")

    class Meta:
        model = PlantPhenology
        fields = []
        exclude = ["created_at", "updated_at"]


class CameratrapFilter(FilterSet):
    observationType = CharFilter(field_name="observationType", lookup_expr="exact")
    observationLevel = CharFilter(field_name="observationLevel", lookup_expr="exact")
    observationComments = CharFilter(
        field_name="observationComments", lookup_expr="exact"
    )
    deploymentID = CharFilter(field_name="deploymentID", lookup_expr="exact")
    eventStartDate = DateFilter(field_name="eventDate", lookup_expr="gte")
    eventEndDate = DateFilter(field_name="eventDate", lookup_expr="lte")
    locationRemarks = CharFilter(field_name="locationRemarks", lookup_expr="exact")
    scientificName = CharFilter(field_name="scientificName", lookup_expr="exact")
    scientificNameAuthorship = CharFilter(
        field_name="scientificNameAuthorship", lookup_expr="exact"
    )
    scientificNameID = CharFilter(field_name="scientificNameID", lookup_expr="exact")
    vernacularName = CharFilter(field_name="vernacularName", lookup_expr="exact")
    taxonID = CharFilter(field_name="taxonID", lookup_expr="exact")
    taxonRank = CharFilter(field_name="taxonRank", lookup_expr="exact")
    family = CharFilter(field_name="family", lookup_expr="exact")
    familyChinese = CharFilter(field_name="familyChinese", lookup_expr="exact")
    fileName = CharFilter(field_name="fileName", lookup_expr="exact")
    filePath = CharFilter(field_name="filePath", lookup_expr="exact")
    filePublic = BooleanFilter(field_name="filePublic", lookup_expr="exact")
    fileMediatype = CharFilter(field_name="fileMediatype", lookup_expr="exact")
    observationID = CharFilter(field_name="observationID", lookup_expr="exact")
    sex = CharFilter(field_name="sex", lookup_expr="exact")
    locationID = CharFilter(field_name="locationID", lookup_expr="exact")

    class Meta:
        model = Cameratrap
        fields = []
        exclude = ["created_at", "updated_at"]


class TerreSoundIndexFilter(FilterSet):
    dataID = CharFilter(field_name="dataID", lookup_expr="exact")
    eventID = CharFilter(field_name="eventID", lookup_expr="exact")
    sh = NumberFilter(field_name="sh", lookup_expr="exact")
    th = NumberFilter(field_name="th", lookup_expr="exact")
    H = NumberFilter(field_name="H", lookup_expr="exact")
    ACI = NumberFilter(field_name="ACI", lookup_expr="exact")
    ADI = NumberFilter(field_name="ADI", lookup_expr="exact")
    AEI = NumberFilter(field_name="AEI", lookup_expr="exact")
    BI = NumberFilter(field_name="BI", lookup_expr="exact")
    NDSI = NumberFilter(field_name="NDSI", lookup_expr="exact")
    associatedMedia = CharFilter(field_name="associatedMedia", lookup_expr="exact")
    measurementStartDate = DateFilter(
        field_name="measurementDeterminedDate",
        lookup_expr="gte",
    )
    measurementEndDate = DateFilter(
        field_name="measurementDeterminedDate",
        lookup_expr="lte",
    )
    locationID = CharFilter(field_name="locationID", lookup_expr="exact")
    deploymentID = CharFilter(field_name="deploymentID", lookup_expr="exact")

    class Meta:
        model = TerreSoundIndex
        fields = []
        exclude = ["created_at", "updated_at"]


class BirdnetSoundFilter(FilterSet):
    dataID = CharFilter(field_name="dataID", lookup_expr="exact")
    eventID = CharFilter(field_name="eventID", lookup_expr="exact")
    vernacularName = CharFilter(field_name="vernacularName", lookup_expr="exact")
    model = CharFilter(field_name="model", lookup_expr="exact")
    time_begin = NumberFilter(field_name="time_begin", lookup_expr="exact")
    time_end = NumberFilter(field_name="time_end", lookup_expr="exact")
    confidence = NumberFilter(field_name="confidence", lookup_expr="exact")
    associatedMedia = CharFilter(field_name="associatedMedia", lookup_expr="exact")
    measurementStartDate = DateFilter(
        field_name="measurementDeterminedDate",
        lookup_expr="gte",
    )
    measurementEndDate = DateFilter(
        field_name="measurementDeterminedDate",
        lookup_expr="lte",
    )
    locationID = CharFilter(field_name="locationID", lookup_expr="exact")
    deploymentID = CharFilter(field_name="deploymentID", lookup_expr="exact")
    taxonID = CharFilter(field_name="taxonID", lookup_expr="exact")
    scientificName = CharFilter(field_name="scientificName", lookup_expr="exact")
    taxonRank = CharFilter(field_name="taxonRank", lookup_expr="exact")
    scientificNameID = NumberFilter(field_name="scientificNameID", lookup_expr="exact")
    family = CharFilter(field_name="family", lookup_expr="exact")
    familyChinese = CharFilter(field_name="familyChinese", lookup_expr="exact")

    class Meta:
        model = BirdnetSound
        fields = []
        exclude = ["created_at", "updated_at"]


class WeatherFilter(FilterSet):
    dataID = CharFilter(field_name="dataID", lookup_expr="exact")
    eventID = CharFilter(field_name="eventID", lookup_expr="exact")
    locationID = CharFilter(field_name="locationID", lookup_expr="exact")
    deploymentID = CharFilter(field_name="deploymentID", lookup_expr="exact")
    eventDate = DateFilter(field_name="eventDate", lookup_expr="exact")
    eventStartDate = DateFilter(field_name="eventDate", lookup_expr="gte")
    eventEndDate = DateFilter(field_name="eventDate", lookup_expr="lte")
    eventTime = CharFilter(field_name="eventTime", lookup_expr="exact")

    PAR = NumberFilter(field_name="PAR", lookup_expr="exact")
    WetnessLevel = NumberFilter(field_name="WetnessLevel", lookup_expr="exact")
    AirTemperature = NumberFilter(field_name="AirTemperature", lookup_expr="exact")
    RelativeHumidity = NumberFilter(field_name="RelativeHumidity", lookup_expr="exact")
    AirPressure = NumberFilter(field_name="AirPressure", lookup_expr="exact")
    WaterContent = NumberFilter(field_name="WaterContent", lookup_expr="exact")
    SoilTemperature = NumberFilter(field_name="SoilTemperature", lookup_expr="exact")
    WindDirection = NumberFilter(field_name="WindDirection", lookup_expr="exact")
    WindSpeed = NumberFilter(field_name="WindSpeed", lookup_expr="exact")
    GustSpeed = NumberFilter(field_name="GustSpeed", lookup_expr="exact")
    Precipitation = NumberFilter(field_name="Precipitation", lookup_expr="exact")

    class Meta:
        model = Weather
        fields = []
        exclude = ["created_at", "updated_at"]
