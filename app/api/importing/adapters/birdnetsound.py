from api.importing.adapters.base import BaseImportAdapter
from api.importing.mappings.birdnetsound_mapping import build_birdnetsound_payload
from api.models import BirdnetSound


DEFAULT_BIRDNETSOUND_HASH_FIELDS = [
    "dataID",
    "eventID",
    "vernacularName",
    "model",
    "time_begin",
    "time_end",
    "confidence",
    "associatedMedia",
    "measurementDeterminedDate",
    "locationID",
    "deploymentID",
    "taxonID",
    "scientificName",
    "taxonRank",
    "scientificNameID",
    "family",
    "familyChinese",
]


class BirdNetSoundDataAdapter(BaseImportAdapter):
    model = BirdnetSound
    key_field = "dataID"
    hash_fields = DEFAULT_BIRDNETSOUND_HASH_FIELDS
    payload_builder = staticmethod(build_birdnetsound_payload)
