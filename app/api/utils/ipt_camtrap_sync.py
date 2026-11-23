"""Camtrap conversion and manual IPT synchronization, independent of API views."""

from datetime import datetime
from zoneinfo import ZoneInfo

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from api.models import (
    Cameratrap,
    IptCamtrapDeployment,
    IptCamtrapMedia,
    IptCamtrapObservation,
    Location,
)


MODELS = {
    "observations": IptCamtrapObservation,
    "media": IptCamtrapMedia,
    "deployments": IptCamtrapDeployment,
}


def convert_camtrap_rows(rows, locations, source_timezone="Asia/Taipei"):
    """Build validated payloads without saving models.

    ``locations`` maps location_id to a list, because api_location does not enforce
    uniqueness. Naive source event times are interpreted in source_timezone.
    """
    tz = ZoneInfo(source_timezone)
    result = {name: [] for name in MODELS}
    errors = []
    grouped = {}
    candidates = {"observations": {}, "media": {}}
    conflicts = {"observations": set(), "media": set()}
    source_records = animal_records = 0

    def error(table, identifier, message):
        errors.append({"table": table, "id": str(identifier), "error": message})

    def validate(table, payload):
        identifier = payload.get({"observations": "observationID", "media": "mediaID",
                                  "deployments": "deploymentID"}[table])
        cleaned = {}
        valid = True
        for field in MODELS[table]._meta.fields:
            if field.primary_key:
                continue
            try:
                value = payload.get(field.name)
                if not field.blank and isinstance(value, str) and not value.strip():
                    raise ValidationError("必填欄位不可為空白")
                cleaned[field.name] = field.clean(value, None)
            except ValidationError as exc:
                error(table, identifier, f"{field.name}: {'; '.join(exc.messages)}")
                valid = False
        return cleaned if valid else None

    def collect(table, identifier, payload):
        if identifier in candidates[table] and candidates[table][identifier] != payload:
            if identifier not in conflicts[table]:
                error(table, identifier, "同一識別碼對應不同資料，已排除所有衝突版本")
            conflicts[table].add(identifier)
        else:
            candidates[table][identifier] = payload

    for row in rows:
        if row.observationType != Cameratrap.ANIMAL:
            continue
        source_records += 1
        animal_records += 1
        if not row.deploymentID or not row.deploymentID.strip():
            error("source", row.pk, "缺少 deploymentID")
            continue
        group = grouped.setdefault(row.deploymentID, {
            "times": [], "location_ids": set(), "invalid_time": False,
        })
        group["location_ids"].add(row.locationID)
        try:
            stamp = datetime.combine(row.eventDate, row.eventTime)
            if timezone.is_naive(stamp):
                stamp = timezone.make_aware(stamp, tz)
            group["times"].append(stamp)
        except (TypeError, ValueError) as exc:
            group["invalid_time"] = True
            error("source", row.pk, f"無效 eventDate/eventTime: {exc}")
            continue

        media_id = f"{row.observationID}_{row.fileName or ''}" if row.observationID else None
        collect("media", media_id, {
            "mediaID": media_id,
            "deploymentID": row.deploymentID,
            "captureMethod": "activityDetection",
            "timestamp": stamp,
            "filePath": row.filePath,
            "filePublic": row.filePublic,
            "fileName": row.fileName,
            "fileMediatype": row.fileMediatype,
        })
        collect("observations", row.observationID, {
            "observationID": row.observationID,
            "deploymentID": row.deploymentID,
            "eventStart": stamp,
            "eventEnd": stamp,
            "observationLevel": row.observationLevel,
            "observationType": row.observationType,
            "scientificName": row.scientificName,
            "sex": row.sex,
            "classificationMethod": "human",
        })

    valid_deployments = set()
    for deployment_id, group in grouped.items():
        if group["invalid_time"] or not group["times"]:
            error("deployments", deployment_id, "時間資料不完整，無法計算部署起訖")
            continue
        if len(group["location_ids"]) != 1:
            error("deployments", deployment_id, "同一 deploymentID 對應多個 locationID")
            continue
        location_id = next(iter(group["location_ids"]))
        matches = locations.get(location_id, [])
        if len(matches) != 1:
            error("deployments", deployment_id,
                  f"locationID={location_id!r} 對應 {len(matches)} 筆 Location，必須恰為一筆")
            continue
        location = matches[0]
        payload = validate("deployments", {
            "deploymentID": deployment_id,
            "locationID": location_id,
            "locationName": location.location_name,
            "latitude": location.decimal_latitude,
            "longitude": location.decimal_longitude,
            "deploymentStart": min(group["times"]),
            "deploymentEnd": max(group["times"]),
        })
        if payload is not None:
            result["deployments"].append(payload)
            valid_deployments.add(deployment_id)

    for table in candidates:
        for identifier, payload in candidates[table].items():
            if identifier in conflicts[table]:
                continue
            cleaned = validate(table, payload)
            if cleaned is not None and payload["deploymentID"] in valid_deployments:
                result[table].append(cleaned)

    return {
        "dry_run": True,
        "source_timezone": source_timezone,
        "source_records": source_records,
        "animal_records": animal_records,
        "counts": {name: len(payloads) for name, payloads in result.items()},
        "errors": errors,
        "payloads": result,
    }


def sync_camtrap(*, dry_run=False, truncate=False, limit=None, deployment_id=None,
                 source_timezone="Asia/Taipei"):
    """Synchronize animal records, or preview without writing.

    A limit selects deployment IDs after filtering animals, rather than rows.
    Deployment time ranges are derived only from those animal records.
    """
    if limit is not None and (isinstance(limit, bool) or not isinstance(limit, int) or limit < 1):
        raise ValueError("limit 必須為正整數（部署數量）")
    if not isinstance(dry_run, bool) or not isinstance(truncate, bool):
        raise ValueError("dry_run 與 truncate 必須為布林值")
    source = Cameratrap.objects.filter(observationType=Cameratrap.ANIMAL)
    if deployment_id is not None:
        source = source.filter(deploymentID=deployment_id)
    if limit is not None:
        ids = list(source.order_by("deploymentID").values_list("deploymentID", flat=True).distinct()[:limit])
        source = source.filter(deploymentID__in=ids)
    location_ids = source.order_by().values_list("locationID", flat=True).distinct()
    locations = {}
    for location in Location.objects.filter(location_id__in=location_ids).order_by("pk"):
        locations.setdefault(location.location_id, []).append(location)
    result = convert_camtrap_rows(
        source.order_by("deploymentID", "pk").iterator(), locations, source_timezone
    )
    result.update(dry_run=dry_run, truncate=truncate)
    result["created"] = {name: 0 for name in MODELS}
    result["updated"] = {name: 0 for name in MODELS}
    result["synced"] = {name: 0 for name in MODELS}
    # A failed conversion must not truncate targets or partially update them.
    if result["errors"] and not dry_run:
        result["write_skipped"] = True
        return result

    identifiers = {"observations": "observationID", "media": "mediaID",
                   "deployments": "deploymentID"}

    if dry_run:
        for name, model in MODELS.items():
            key = identifiers[name]
            requested = [row[key] for row in result["payloads"][name]]
            existing = set() if truncate else set(
                model.objects.filter(**{f"{key}__in": requested}).values_list(key, flat=True)
            )
            result["updated"][name] = len(existing)
            result["created"][name] = len(requested) - len(existing)
        return result

    with transaction.atomic():
        if truncate:
            for model in MODELS.values():
                model.objects.all().delete()
        for name in ("deployments", "media", "observations"):
            key = identifiers[name]
            for payload in result["payloads"][name]:
                defaults = payload.copy()
                identifier = defaults.pop(key)
                _, created = MODELS[name].objects.update_or_create(
                    **{key: identifier}, defaults=defaults
                )
                result["created" if created else "updated"][name] += 1
                result["synced"][name] += 1
    return result
