from api.importing.adapters.base import BaseImportAdapter
from api.importing.mappings.biosound_mapping import build_biosound_payload
from api.models import BioSound


DEFAULT_BIOSOUND_HASH_FIELDS = [
    "dataID",
    "eventID",
    "classid",
    "scientificName",
    "taxonRank",
    "vernacularName",
    "soundclass",
    "time_begin",
    "time_end",
    "confidence",
    "associatedMedia",
    "freq_low",
    "freq_high",
    "measurementDeterminedDate",
    "locationID",
]


class BioSoundDataAdapter(BaseImportAdapter):
    model = BioSound
    key_field = "dataID"
    hash_fields = DEFAULT_BIOSOUND_HASH_FIELDS
    payload_builder = staticmethod(build_biosound_payload)
