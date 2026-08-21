from api.importing.adapters.base import BaseImportAdapter
from api.importing.mappings.cameratrap_mapping import build_cameratrap_payload
from api.models import Cameratrap


DEFAULT_CAMERATRAP_HASH_FIELDS = [
    "observationID",
    "observationType",
    "observationLevel",
    "observationComments",
    "deploymentID",
    "timestamp",
    "eventDate",
    "eventTime",
    "locationRemarks",
    "scientificName",
    "scientificNameAuthorship",
    "scientificNameID",
    "vernacularName",
    "taxonID",
    "taxonRank",
    "family",
    "familyChinese",
    "fileName",
    "filePath",
    "filePublic",
    "fileMediatype",
    "sex",
    "locationID",
]


class CameratrapDataAdapter(BaseImportAdapter):
    model = Cameratrap
    key_field = "observationID"
    hash_fields = DEFAULT_CAMERATRAP_HASH_FIELDS
    payload_builder = staticmethod(build_cameratrap_payload)
