from datetime import datetime


def optional_date(value, field_name, record, errors, validators):
    if value in (None, "", "null"):
        return None
    return validators["event_date"](value, field_name, record, errors)


def optional_datetime(value, field_name, record, errors, validators):
    if value in (None, "", "null"):
        return None
    return validators["event_datetime"](value, field_name, record, errors)


def optional_time(value, field_name, errors):
    if value in (None, "", "null"):
        return None

    if hasattr(value, "hour") and hasattr(value, "minute"):
        return value

    s = str(value).strip()
    if s.endswith("Z"):
        s = s[:-1]

    for fmt in ("%H:%M:%S", "%H:%M:%S.%f", "%H:%M"):
        try:
            return datetime.strptime(s, fmt).time()
        except ValueError:
            pass

    errors.append(
        {
            "field": field_name,
            "error": "invalid_format",
            "value": value,
            "expected": "HH:MM[:SS]",
        }
    )
    return None


def required_time(value, field_name, errors):
    if value in (None, "", "null"):
        errors.append({"field": field_name, "error": "required"})
        return None
    return optional_time(value, field_name, errors)
