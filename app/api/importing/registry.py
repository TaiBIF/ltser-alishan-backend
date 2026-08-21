import re
from api.importing.adapters.biosound import BioSoundDataAdapter
from api.importing.adapters.birdnetsound import BirdNetSoundDataAdapter
from api.importing.adapters.cameratrap import CameratrapDataAdapter
from api.importing.adapters.plantphenology import PlantPhenologyDataAdapter
from api.importing.adapters.terresoundindex import TerreSoundIndexDataAdapter
from api.importing.adapters.weather import WeatherDataAdapter

ADAPTERS = {
    "ltser-indigenous-alishan-cameratrap": CameratrapDataAdapter,
    "ltser-indigenous-alishan-plantphenology": PlantPhenologyDataAdapter,
    "ltser-indigenous-terresoundindex": TerreSoundIndexDataAdapter,
    "ltser-indigenous-birdnetsound": BirdNetSoundDataAdapter,
    "ltser-indigenous-biosound": BioSoundDataAdapter,
    "ltser-indigenous-weather": WeatherDataAdapter,
}


def normalize_package_name(package_name: str) -> str:
    return re.sub(r"-\d{6}$", "", package_name)
