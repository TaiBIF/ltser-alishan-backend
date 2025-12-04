from .models import *

OBS_CONFIG = {
    "plantphenology": {
        "label": "植物物候",
        "model": PlantPhenology,  # 觀測資料 model
        "datafield_model": PlantPhenologyDataField,  # 資料欄位 model
        "date_field": "eventDate",
    },
    "cameratrap": {
        "label": "自動照相機監測",
        "model": Cameratrap,
        "datafield_model": CameratrapDataField,
        "date_field": "eventDate",
    },
    "terresoundindex": {
        "label": "聲音指數",
        "model": TerreSoundIndex,
        "datafield_model": TerreSoundIndexDataField,
        "date_field": "measurementDeterminedDate",
    },
    "birdnetsound": {
        "label": "鳥音辨識",
        "model": BirdnetSound,
        "datafield_model": BirdnetSoundDataField,
        "date_field": "measurementDeterminedDate",
    },
    "biosound": {
        "label": "生物辨識",
        "model": BioSound,
        "datafield_model": BioSoundDataField,
        "date_field": "measurementDeterminedDate",
    },
    "weather": {
        "label": "氣象觀測",
        "model": Weather,
        "datafield_model": WeatherDataField,
        "date_field": "eventDate",
    },
}
