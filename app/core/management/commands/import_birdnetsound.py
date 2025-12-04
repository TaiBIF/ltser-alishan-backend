from typing import Dict, Any, List, Iterable, Optional
from decimal import Decimal


import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.dateparse import parse_date, parse_datetime

from api.models import BirdnetSound

CKAN_BASE = "https://data.depositar.io/api/3/action"
CKAN_PACKAGE_SHOW = f"{CKAN_BASE}/package_show"
CKAN_DATASTORE_SEARCH = f"{CKAN_BASE}/datastore_search"


# ---------- HTTP session with retry/backoff ----------
def make_session(total_retries: int = 5, backoff: float = 0.5) -> requests.Session:
    s = requests.Session()
    retry = Retry(
        total=total_retries,
        connect=total_retries,
        read=total_retries,
        status=total_retries,
        status_forcelist=(429, 500, 502, 503, 504, 520, 521, 522, 524),
        allowed_methods=frozenset(["GET", "HEAD"]),
        backoff_factor=backoff,
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry, pool_connections=10, pool_maxsize=10)
    s.mount("http://", adapter)
    s.mount("https://", adapter)
    s.headers.update(
        {
            "User-Agent": "TerrsSoundIndexImporter/1.0",
            "Connection": "keep-alive",
            "Accept": "application/json",
        }
    )
    return s


# ---------- 欄位型別轉換 ----------
def coerce_value(model, field_name: str, value):
    if value is None:
        return None
    if isinstance(value, str):
        v = value.strip()
        if v == "":
            return None
    else:
        v = value

    from django.db import models

    field = model._meta.get_field(field_name)

    if isinstance(field, models.IntegerField):
        try:
            return int(v)
        except Exception:
            return None

    if isinstance(field, (models.FloatField, models.DecimalField)):
        try:
            return float(v)
        except Exception:
            return None

    if isinstance(field, models.BooleanField):
        if isinstance(v, bool):
            return v
        sv = str(v).lower()
        if sv in ("1", "true", "t", "yes", "y"):
            return True
        if sv in ("0", "false", "f", "no", "n"):
            return False
        return None

    if isinstance(field, models.DateField) and not isinstance(v, (int, float)):
        d = parse_date(str(v))
        if d:
            return d
        dt = parse_datetime(str(v))
        return dt.date() if dt else None

    if isinstance(field, models.DateTimeField) and not isinstance(v, (int, float)):
        return parse_datetime(str(v))

    return str(v)


def filter_row_to_model_fields(model, row: Dict[str, Any]) -> Dict[str, Any]:
    """
    取出 API record 中在模型裡存在的欄位並做型別轉換。
    前提：API 欄名 = 模型欄位名。
    """
    model_fields = {f.name for f in model._meta.get_fields() if hasattr(f, "attname")}
    out = {}
    for key, val in row.items():
        if key in model_fields:
            out[key] = coerce_value(model, key, val)
    return out


# ---------- 先用 package_show 取得所有 resource_id ----------
def fetch_package_resource_ids(
    session: requests.Session,
    package_id: str,
    formats: Optional[List[str]] = None,
    include_non_datastore: bool = False,
    timeout: int = 60,
) -> List[Dict[str, Any]]:
    """
    回傳符合條件的資源清單，每個元素至少包含 {'id': <id>, 'name': <name>, 'format': <format>, 'datastore_active': bool}
    - formats: 例如 ["CSV", "JSON"]。大小寫不敏感。
    - include_non_datastore: True 則不過濾 datastore_active；False 只要 datastore_active=True
    """
    r = session.get(CKAN_PACKAGE_SHOW, params={"id": package_id}, timeout=timeout)
    if r.status_code != 200:
        raise CommandError(f"package_show failed: HTTP {r.status_code}")
    data = r.json()
    resources = (data.get("result") or {}).get("resources") or []

    out = []
    fmt_set = {f.upper() for f in formats} if formats else None
    for res in resources:
        rid = res.get("id")
        name = res.get("name") or rid
        fmt = (res.get("format") or "").upper()
        ds_active = bool(res.get("datastore_active"))
        if not include_non_datastore and not ds_active:
            continue
        if fmt_set and fmt not in fmt_set:
            continue
        out.append(
            {
                "id": rid,
                "name": name,
                "format": fmt,
                "datastore_active": ds_active,
            }
        )
    return out


# ---------- 逐批拉 Datastore records ----------
def datastore_search_batches(
    session: requests.Session,
    resource_id: str,
    limit: int = 1000,
    timeout: int = 120,
    max_records: Optional[int] = None,
    **query_params,
) -> Iterable[List[Dict[str, Any]]]:
    """
    用 CKAN datastore_search 把資料分批取回（每次 yield 一個批次的 records list）。
    - limit: 每批筆數
    - max_records: 本次最多處理總筆數；None 則抓全量
    """
    offset = 0
    pulled = 0

    while True:
        params = {
            "resource_id": resource_id,
            "limit": limit,
            "offset": offset,
            **query_params,
        }
        r = session.get(CKAN_DATASTORE_SEARCH, params=params, timeout=timeout)
        if r.status_code != 200:
            raise CommandError(
                f"datastore_search failed: HTTP {r.status_code} (offset={offset})"
            )

        data = r.json()
        result = data.get("result") or {}
        records = result.get("records") or []

        if not records:
            break

        yield records

        pulled += len(records)
        if max_records is not None and pulled >= max_records:
            break

        offset += len(records)


class Command(BaseCommand):
    help = (
        "由 package_show 取得所有資源，再用 datastore_search 分批拉取，"
        "每批立即 upsert 到 BirdnetSound。"
    )

    def add_arguments(self, parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            "--package-id",
            help="CKAN package_id（先抓所有 resource，再逐一同步）",
        )
        group.add_argument(
            "--resource-id",
            help="直接指定單一 datastore resource_id（跳過 package_show）",
        )

        parser.add_argument(
            "--unique-fields",
            required=True,
            help="以逗號分隔的自然鍵欄位（例如：eventID,dataID）",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=1000,
            help="每批抓取的筆數（limit），預設 1000",
        )
        parser.add_argument(
            "--timeout",
            type=int,
            default=120,
            help="HTTP 逾時秒數，預設 120",
        )
        parser.add_argument(
            "--max-records",
            type=int,
            help="本次最多處理筆數（測試/保護用）；不設定代表抓全量",
        )
        parser.add_argument(
            "--formats",
            help="只同步指定格式的資源，多個以逗號分隔（例如 CSV,json）；預設不限制",
        )
        parser.add_argument(
            "--include-non-datastore",
            action="store_true",
            help="包含非 datastore_active 的資源（預設不包含）",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="僅計算 insert/update，不寫入資料庫",
        )

    def handle(self, *args, **opts):
        unique_fields = [
            x.strip() for x in opts["unique_fields"].split(",") if x.strip()
        ]
        if not unique_fields:
            raise CommandError(
                "請提供 --unique-fields，例如：--unique-fields eventID,dataID"
            )

        limit: int = opts["limit"]
        timeout: int = opts["timeout"]
        max_records: Optional[int] = opts.get("max_records")
        dry_run: bool = opts["dry_run"]

        formats_opt = opts.get("formats")
        formats: Optional[List[str]] = None
        if formats_opt:
            formats = [f.strip().upper() for f in formats_opt.split(",") if f.strip()]

        session = make_session()

        # 取得資源清單
        resources: List[Dict[str, Any]] = []
        if opts.get("resource_id"):
            resources = [
                {
                    "id": opts["resource_id"],
                    "name": opts["resource_id"],
                    "format": "",
                    "datastore_active": True,  # 既然直接指定，就當作要抓
                }
            ]
            self.stdout.write(f"Using single resource_id: {opts['resource_id']}")
        else:
            package_id: str = opts["package_id"]
            self.stdout.write(f"Fetching resources from package: {package_id}")
            resources = fetch_package_resource_ids(
                session=session,
                package_id=package_id,
                formats=formats,
                include_non_datastore=opts["include_non_datastore"],
                timeout=timeout,
            )
            if not resources:
                raise CommandError("No matching resources found in package.")

        self.stdout.write("-" * 60)
        self.stdout.write(f"Model: {BirdnetSound._meta.label}")
        if opts.get("package_id"):
            self.stdout.write(f"Package ID: {opts['package_id']}")
        self.stdout.write(f"Unique fields: {unique_fields}")
        self.stdout.write(f"Batch limit: {limit}, Max records: {max_records or 'ALL'}")
        self.stdout.write(f"Resources to sync: {len(resources)}")

        total_rows = 0
        total_inserts = 0
        total_updates = 0

        # 逐個 resource 分批處理（每批一個 transaction）
        for res in resources:
            rid = res["id"]
            name = res.get("name") or rid
            self.stdout.write(self.style.HTTP_INFO(f"Sync resource [{name}] ({rid})"))

            for records in datastore_search_batches(
                session=session,
                resource_id=rid,
                limit=limit,
                timeout=timeout,
                max_records=max_records,
            ):
                batch_rows = len(records)
                total_rows += batch_rows
                inserted = 0
                updated = 0

                with transaction.atomic():
                    for row in records:
                        values = filter_row_to_model_fields(BirdnetSound, row)
                        if not values:
                            continue

                        lon = values.get("decimalLongitude")
                        lat = values.get("decimalLatitude")
                        if lon is not None and (
                            lon <= Decimal(-180) or lon >= Decimal(180)
                        ):
                            self.stdout.write(
                                self.style.WARNING(f"Skip bad lon: {lon} row={row}")
                            )
                            continue
                        if lat is not None and (
                            lat <= Decimal(-90) or lat >= Decimal(90)
                        ):
                            self.stdout.write(
                                self.style.WARNING(f"Skip bad lat: {lat} row={row}")
                            )
                            continue

                        lookup = {k: values.get(k) for k in unique_fields}
                        if any(v is None for v in lookup.values()):
                            self.stdout.write(
                                self.style.WARNING(
                                    f"Skip row missing unique fields: {lookup}"
                                )
                            )
                            continue

                        defaults = {
                            k: v for k, v in values.items() if k not in unique_fields
                        }

                        if dry_run:
                            exists = BirdnetSound.objects.filter(**lookup).exists()
                            if exists:
                                updated += 1
                            else:
                                inserted += 1
                            continue

                        obj, created = BirdnetSound.objects.update_or_create(
                            **lookup, defaults=defaults
                        )
                        if created:
                            inserted += 1
                        else:
                            updated += 1

                total_inserts += inserted
                total_updates += updated
                self.stdout.write(
                    self.style.HTTP_INFO(
                        f"Batch committed: rows={batch_rows}, inserted={inserted}, updated={updated}, total_so_far={total_rows}"
                    )
                )

        self.stdout.write("-" * 60)
        self.stdout.write(
            self.style.SUCCESS(
                f"ALL DONE. total_rows={total_rows}, total_inserted={total_inserts}, total_updated={total_updates}"
            )
        )
