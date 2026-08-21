def _optional_date(value, field_name, record, errors, validators):
    if value in (None, "", "null"):
        return None
    return validators["event_date"](value, field_name, record, errors)


def build_birdnetsound_payload(record, validators):
    """
    將 CKAN datastore record 轉成 BirdnetSound 可用的 payload(dict)。
    回傳：payload, row_errors, row_warnings
    """
    errors = []
    warnings = []

    dataID = validators["required"](record.get("dataID"), "dataID", record, errors)
    eventID = validators["required"](record.get("eventID"), "eventID", record, errors)
    deploymentID = validators["required"](
        record.get("deploymentID"), "deploymentID", record, errors
    )
    scientificName = validators["required"](
        record.get("scientificName"), "scientificName", record, errors
    )

    time_begin = validators["decimal"](
        record.get("time_begin"), "time_begin", record, errors, warnings
    )
    time_end = validators["decimal"](
        record.get("time_end"), "time_end", record, errors, warnings
    )
    confidence = validators["decimal"](
        record.get("confidence"), "confidence", record, errors, warnings
    )
    measurementDeterminedDate = _optional_date(
        record.get("measurementDeterminedDate"),
        "measurementDeterminedDate",
        record,
        errors,
        validators,
    )
    payload = {
        "dataID": dataID,
        "eventID": eventID,
        "vernacularName": record.get("vernacularName"),
        "model": record.get("model"),
        "time_begin": time_begin,
        "time_end": time_end,
        "confidence": confidence,
        "associatedMedia": record.get("associatedMedia"),
        "measurementDeterminedDate": measurementDeterminedDate,
        "locationID": record.get("locationID"),
        "deploymentID": deploymentID,
        "taxonID": record.get("taxonID"),
        "scientificName": scientificName,
        "taxonRank": record.get("taxonRank"),
        "scientificNameID": record.get("scientificNameID"),
        "family": record.get("family"),
        "familyChinese": record.get("familyChinese"),
    }

    return payload, errors, warnings
