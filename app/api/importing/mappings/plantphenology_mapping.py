DECIMAL_FIELDS = [
    "sampleSizeValue",
]

INT_FIELDS = [
    "minimumElevationInMeters",
    "maximumElevationInMeters",
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
]

STRING_FIELDS = [
    "vernacularName",
    "taxonID",
    "scientificName",
    "taxonRank",
    "organismID",
    "samplingProtocol",
    "sampleSizeUnit",
]


def build_plantphenology_payload(record, validators):
    errors = []
    warnings = []

    payload = {
        "dataID": validators["required"](record.get("dataID"), "dataID", record, errors),
        "eventID": validators["required"](
            record.get("eventID"), "eventID", record, errors
        ),
        "eventDate": validators["event_date"](
            record.get("eventDate"), "eventDate", record, errors
        ),
        "verbatimLocality": validators["required"](
            record.get("verbatimLocality"), "verbatimLocality", record, errors
        ),
        "locality": validators["required"](
            record.get("locality"), "locality", record, errors
        ),
        "locationID": validators["required"](
            record.get("locationID"), "locationID", record, errors
        ),
    }

    payload["decimalLongitude"] = validators["coordinate"](
        record.get("decimalLongitude"),
        "decimalLongitude",
        record,
        errors,
        warnings,
        -180,
        180,
    )
    payload["decimalLatitude"] = validators["coordinate"](
        record.get("decimalLatitude"),
        "decimalLatitude",
        record,
        errors,
        warnings,
        -90,
        90,
    )

    for field in DECIMAL_FIELDS:
        payload[field] = validators["decimal"](
            record.get(field), field, record, errors, warnings
        )

    for field in INT_FIELDS:
        payload[field] = validators["int_optional"](
            record.get(field), field, record, errors
        )

    for field in STRING_FIELDS:
        payload[field] = record.get(field)

    payload["animalGrazing"] = validators["boolean_optional"](
        record.get("animalGrazing"), "animalGrazing", record, errors
    )

    return payload, errors, warnings
