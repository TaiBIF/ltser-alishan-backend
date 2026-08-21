INT_FIELDS = ["min"]

DECIMAL_FIELDS = ["sh", "th", "H", "ACI", "ADI", "AEI", "BI", "NDSI", "sec"]


def build_terresoundindex_payload(record, validators):
    errors = []
    warnings = []

    payload = {
        "dataID": validators["required"](record.get("dataID"), "dataID", record, errors),
        "eventID": validators["required"](
            record.get("eventID"), "eventID", record, errors
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
        "deploymentID": validators["required"](
            record.get("deploymentID"), "deploymentID", record, errors
        ),
        "associatedMedia": record.get("associatedMedia"),
    }

    for field in DECIMAL_FIELDS:
        payload[field] = validators["decimal"](
            record.get(field), field, record, errors, warnings
        )

    for field in INT_FIELDS:
        payload[field] = validators["int_optional"](
            record.get(field), field, record, errors
        )

    return payload, errors, warnings
