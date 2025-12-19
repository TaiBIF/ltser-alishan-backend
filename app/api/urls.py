from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *


router = DefaultRouter()
router.register(r"plantphenology", PlantPhenologyViewSet, basename="plant-phenology")
router.register(r"cameratrap", CameratrapViewSet, basename="cameratrap")
router.register(r"terresoundindex", TerreSoundIndexViewSet, basename="terresoundindex")
router.register(r"birdnetsound", BirdnetSoundViewSet, basename="birdnetsound")
router.register(r"biosound", BioSoundViewSet, basename="biosound")
router.register(r"weather", WeatherViewSet, basename="weather")
router.register(r"data-field", DataFieldViewSet, basename="data-field")
router.register(r"location", LocationViewSet, basename="location")


urlpatterns = [
    path(
        "plantphenology/chart/",
        PlantPhenologyChartView.as_view(),
        name="plant-phenology-chart",
    ),
    path(
        "cameratrap/chart/",
        CameratrapChartView.as_view(),
        name="cameratrap-chart",
    ),
    path(
        "birdnetsound/chart/",
        BirdnetSoundChartView.as_view(),
        name="birdnetsound-chart",
    ),
    path(
        "terresoundindex/chart/",
        TerreSoundChartView.as_view(),
        name="terresoundindex-chart",
    ),
    path(
        "biosound/chart/",
        BioSoundChartView.as_view(),
        name="biosound-chart",
    ),
    path(
        "weather/chart/",
        WeatherChartView.as_view(),
        name="weather-chart",
    ),
    path("map/location/", location_map_list, name="map-loacation"),
    path("map/filter/", location_map_filter, name="map-filter"),
    path("download/", request_download, name="request-download"),
    path("download/file/<int:pk>/", download_file, name="download-file"),
    path("segis/village-population/", village_population, name="village-population"),
    path("segis/village-dynamics/", village_dynamics, name="village-dynamics"),
    path("segis/town-pyramid/", town_pyramid, name="town-pyramid"),
    path("segis/town-industry/", town_industry, name="town-industry"),
    path("", include(router.urls)),
]
