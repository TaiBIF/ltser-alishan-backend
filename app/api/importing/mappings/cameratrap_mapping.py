from api.importing.mappings.common import required_time


STRING_FIELDS = [
    "observationComments",
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
    "sex",
]


def build_cameratrap_payload(record, validators):
    errors = []
    warnings = []

    payload = {
        "observationID": validators["required"](
            record.get("observationID"), "observationID", record, errors
        ),
        "observationType": validators["required"](
            record.get("observationType"), "observationType", record, errors
        ),
        "observationLevel": validators["required"](
            record.get("observationLevel"), "observationLevel", record, errors
        ),
        "deploymentID": validators["required"](
            record.get("deploymentID"), "deploymentID", record, errors
        ),
        "timestamp": validators["event_datetime"](
            record.get("timestamp"), "timestamp", record, errors
        ),
        "eventDate": validators["event_date"](
            record.get("eventDate"), "eventDate", record, errors
        ),
        "eventTime": required_time(record.get("eventTime"), "eventTime", errors),
        "fileMediatype": validators["required"](
            record.get("fileMediatype"), "fileMediatype", record, errors
        ),
        "locationID": validators["required"](
            record.get("locationID"), "locationID", record, errors
        ),
    }

    file_public = validators["boolean_optional"](
        record.get("filePublic"), "filePublic", record, errors
    )
    payload["filePublic"] = bool(file_public) if file_public is not None else False

    for field in STRING_FIELDS:
        payload[field] = record.get(field)

    return payload, errors, warnings
