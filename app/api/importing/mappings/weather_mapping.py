DECIMAL_FIELDS = [
    "PAR",
    "WetnessLevel",
    "AirTemperature",
    "RelativeHumidity",
    "AirPressure",
    "WaterContent",
    "SoilTemperature",
    "WindDirection",
    "WindSpeed",
    "GustSpeed",
    "Precipitation",
]


def build_weather_payload(record, validators):
    errors = []
    warnings = []

    payload = {
        "dataID": validators["required"](record.get("dataID"), "dataID", record, errors),
        "eventID": validators["required"](
            record.get("eventID"), "eventID", record, errors
        ),
        "locationID": validators["required"](
            record.get("locationID"), "locationID", record, errors
        ),
        "deploymentID": validators["required"](
            record.get("deploymentID"), "deploymentID", record, errors
        ),
        "eventDate": validators["event_date"](
            record.get("eventDate"), "eventDate", record, errors
        ),
        "eventTime": validators["required"](
            record.get("eventTime"), "eventTime", record, errors
        ),
    }

    for field in DECIMAL_FIELDS:
        payload[field] = validators["decimal"](
            record.get(field), field, record, errors, warnings
        )

    return payload, errors, warnings
