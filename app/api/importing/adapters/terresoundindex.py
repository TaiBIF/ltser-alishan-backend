from api.importing.adapters.base import BaseImportAdapter
from api.importing.mappings.terresoundindex_mapping import (
    build_terresoundindex_payload,
)
from api.models import TerreSoundIndex


DEFAULT_TERRESOUNDINDEX_HASH_FIELDS = [
    "dataID",
    "eventID",
    "sh",
    "th",
    "H",
    "ACI",
    "ADI",
    "AEI",
    "BI",
    "NDSI",
    "associatedMedia",
    "min",
    "sec",
    "measurementDeterminedDate",
    "locationID",
    "deploymentID",
]


class TerreSoundIndexDataAdapter(BaseImportAdapter):
    model = TerreSoundIndex
    key_field = "dataID"
    hash_fields = DEFAULT_TERRESOUNDINDEX_HASH_FIELDS
    payload_builder = staticmethod(build_terresoundindex_payload)
