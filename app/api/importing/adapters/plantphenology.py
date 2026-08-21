from api.importing.adapters.base import BaseImportAdapter
from api.importing.mappings.plantphenology_mapping import (
    build_plantphenology_payload,
)
from api.models import PlantPhenology


DEFAULT_PLANTPHENOLOGY_HASH_FIELDS = [
    "dataID",
    "eventID",
    "eventDate",
    "decimalLongitude",
    "decimalLatitude",
    "minimumElevationInMeters",
    "maximumElevationInMeters",
    "vernacularName",
    "taxonID",
    "verbatimLocality",
    "scientificName",
    "taxonRank",
    "locality",
    "locationID",
    "organismID",
    "samplingProtocol",
    "canopyCoverPercentage",
    "budCoverPercentage",
    "newLeafCoverPercentage",
    "matureLeafCoverPercentage",
    "yellowLeafCoverPercentage",
    "deadLeafCoverPercentage",
    "totalFlowerCount",
    "budFlowerPercentage",
    "fullBloomPercentage",
    "wiltedFlowerPercentage",
    "totalFruitCount",
    "youngFruitPercentage",
    "greenFruitPercentage",
    "ripeFruitPercentage",
    "wiltedFruitPercentage",
    "coverInPercentage",
    "herbaceousPlantHeight",
    "individualCount",
    "fruitCount",
    "flowerCount",
    "budCount",
    "wiltedPercentage",
    "animalGrazing",
    "sampleSizeValue",
    "sampleSizeUnit",
]


class PlantPhenologyDataAdapter(BaseImportAdapter):
    model = PlantPhenology
    key_field = "dataID"
    hash_fields = DEFAULT_PLANTPHENOLOGY_HASH_FIELDS
    payload_builder = staticmethod(build_plantphenology_payload)
