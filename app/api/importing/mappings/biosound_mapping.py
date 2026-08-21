INT_FIELDS = ["classid"]

DECIMAL_FIELDS = ["time_begin", "time_end", "confidence", "freq_low", "freq_high"]

STRING_FIELDS = ["vernacularName", "soundclass", "associatedMedia"]


def build_biosound_payload(record, validators):
    errors = []
    warnings = []

    payload = {
        "dataID": validators["required"](record.get("dataID"), "dataID", record, errors),
        "eventID": validators["required"](
            record.get("eventID"), "eventID", record, errors
        ),
        "scientificName": validators["required"](
            record.get("scientificName"), "scientificName", record, errors
        ),
        "taxonRank": validators["required"](
            record.get("taxonRank"), "taxonRank", record, errors
        ),
        "measurementDeterminedDate": validators["event_date"](
            record.get("measurementDeterminedDate"),
            "measurementDeterminedDate",
            record,
            errors,
        ),
        "locationID": validators["required"](
            record.get("locationID"), "locationID", record, errors
        ),
    }

    for field in INT_FIELDS:
        payload[field] = validators["int_optional"](
            record.get(field), field, record, errors
        )

    for field in DECIMAL_FIELDS:
        payload[field] = validators["decimal"](
            record.get(field), field, record, errors, warnings
        )

    for field in STRING_FIELDS:
        payload[field] = record.get(field)

    return payload, errors, warnings
