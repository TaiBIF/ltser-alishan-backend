from api.importing.adapters.base import BaseImportAdapter
from api.importing.mappings.weather_mapping import build_weather_payload
from api.models import Weather


DEFAULT_WEATHER_HASH_FIELDS = [
    "dataID",
    "eventID",
    "locationID",
    "deploymentID",
    "eventDate",
    "eventTime",
    "PAR",
    "WetnessLevel",
    "AirTemperature",
    "RelativeHumidity",
    "AirPressure",
    "WaterContent",
    "SoilTemperature",
    "WindDirection",
    "WindSpeed",
    "GustSpeed",
    "Precipitation",
]


class WeatherDataAdapter(BaseImportAdapter):
    model = Weather
    key_field = "dataID"
    hash_fields = DEFAULT_WEATHER_HASH_FIELDS
    payload_builder = staticmethod(build_weather_payload)
