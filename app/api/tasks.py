import os
import csv
import io
import zipfile
import requests
from collections import defaultdict
from datetime import datetime, timedelta
from datetime import datetime
from celery import shared_task

from django.core.cache import cache
from django.conf import settings
from django.core.mail import EmailMessage
from django.urls import reverse
from django.utils import timezone

from api.importing.importer import import_ckan_resource
from api.importing.registry import ADAPTERS

from .utils.cache_keys import (
    location_map_list_key,
    location_map_filter_key,
    segis_cache_key,
)
from .utils.transform_segis_data import (
    transform_population,
    transform_dynamics,
    transform_pyramid,
    transform_industry,
)
from .utils.call_segis import (
    get_latest_time_list,
    get_population_data,
    get_industry_data,
)
from .utils.download import build_obs_maps

from .models import Location, DownloadRequest
from .serializers import LocationMapSerializer
from .obs_config import OBS_CONFIG

ERROR_PROBLEM_LABELS = {
    # 通用
    "required": "必填欄位缺值（不可為空白）",
    # 數值/整數
    "not_a_number": "資料非數值（無法解析成數字）",
    "invalid_number": "數值不合法（NaN 或無限大，無法作為有效數字）",
    "nan": "數值為 NaN（非有效數字）",
    "infinite": "數值為無限大（Inf/-Inf，非有效數字）",
    "not_integer": "資料非整數（必須為整數）",
    "out_of_range": "數值超出允許範圍",
    # 日期/時間
    "invalid_format": "格式不正確（建議使用 YYYY-MM-DD 格式）",
    "invalid_date": "日期不合法（非有效日期）",
    # 布林
    "not_boolean": "資料非布林值（需為 True/False 或 0/1、是/否）",
}

ERROR_FIELD_PROBLEM_LABELS = {
    ("decimalLongitude", "out_of_range"): "經度超出允許範圍（需介於 -180 到 180）",
    ("decimalLatitude", "out_of_range"): "緯度超出允許範圍（需介於 -90 到 90）",
}


@shared_task
def rebuild_location_map_filter_cache():
    year_map = defaultdict(set)

    for code, cfg in OBS_CONFIG.items():
        model = cfg["model"]
        date_field = cfg["date_field"]

        year_dates = model.objects.dates(date_field, "year", order="ASC")
        for d in year_dates:
            year = d.year
            year_map[year].add(code)

    result = {
        str(year): [OBS_CONFIG[code]["label"] for code in sorted(obs_codes)]
        for year, obs_codes in sorted(year_map.items())
    }

    cache.set(location_map_filter_key(), result, timeout=None)


@shared_task
def rebuild_location_map_list_cache():
    year = None
    item = None

    obs_codes = list(OBS_CONFIG.keys())
    locations = Location.objects.order_by("location_id").distinct("location_id")
    result = []

    for loc in locations:
        base = LocationMapSerializer(loc).data
        years_map = defaultdict(list)

        for code in obs_codes:
            cfg = OBS_CONFIG[code]
            model = cfg["model"]
            date_field = cfg["date_field"]

            qs = model.objects.filter(locationID=loc.location_id)
            year_dates = qs.dates(date_field, "year", order="ASC")
            for d in year_dates:
                y = d.year
                years_map[y].append(cfg["label"])

        base["years"] = {str(y): items for y, items in sorted(years_map.items())}
        result.append(base)

    cache.set(location_map_list_key(year, item), result, timeout=None)


@shared_task
def generate_download_zip(download_request_id):
    dl = DownloadRequest.objects.get(id=download_request_id)

    if dl.status not in [DownloadRequest.STATUS_PENDING, DownloadRequest.STATUS_FAILED]:
        return

    dl.status = DownloadRequest.STATUS_PROCESSING
    dl.save(update_fields=["status"])

    try:
        label_to_code, _ = build_obs_maps()

        requested_labels = dl.items or []
        if not isinstance(requested_labels, list) or not requested_labels:
            raise ValueError("items 必須為非空陣列")

        # dl.items 已統一存 label
        obs_codes = []
        for label in requested_labels:
            if isinstance(label, str) and label in label_to_code:
                obs_codes.append(label_to_code[label])

        obs_codes = [c for c in dict.fromkeys(obs_codes) if c in OBS_CONFIG]
        if not obs_codes:
            raise ValueError("沒有有效的觀測項目可供匯出（items 與 OBS_CONFIG 不一致）")

        base_dir = getattr(settings, "MEDIA_ROOT", None)
        if not base_dir:
            raise ValueError("MEDIA_ROOT 尚未設定")

        download_dir = os.path.join(base_dir, "downloads", str(dl.id))
        os.makedirs(download_dir, exist_ok=True)

        csv_files = []

        # selected：樣站 + 年份 + 多個觀測項目 => 每一個觀測項目產生各自的 CSV
        if dl.mode == DownloadRequest.MODE_SELECTED:
            if not dl.location_id or not dl.year:
                raise ValueError("selected 模式必須提供 location_id 與 year")

            for code in obs_codes:
                cfg = OBS_CONFIG[code]
                model = cfg["model"]
                date_field = cfg["date_field"]

                qs = model.objects.filter(locationID=dl.location_id)
                qs = qs.filter(**{f"{date_field}__year": dl.year})

                if not qs.exists():
                    continue

                filename = f"{code}_{dl.year}_{dl.location_id}.csv"
                file_path = os.path.join(download_dir, filename)

                field_names = [f.name for f in model._meta.fields]

                with open(file_path, "w", newline="", encoding="utf-8-sig") as f:
                    writer = csv.writer(f)
                    writer.writerow(field_names)
                    for obj in qs.iterator():
                        writer.writerow([getattr(obj, field) for field in field_names])

                csv_files.append((filename, file_path))

        # item_all：單一觀測項目 => 產生單一個大 CSV，包含全樣站全年度
        elif dl.mode == DownloadRequest.MODE_ITEM_ALL:
            if len(obs_codes) != 1:
                raise ValueError("item_all 模式 items 只能包含 1 個項目")

            code = obs_codes[0]
            cfg = OBS_CONFIG[code]
            model = cfg["model"]

            qs = model.objects.all()
            if not qs.exists():
                raise ValueError(f"{code} 全域資料為空，未產生任何 CSV 檔案")

            filename = f"{code}_ALL_YEARS_ALL_LOCATIONS.csv"
            file_path = os.path.join(download_dir, filename)

            field_names = [f.name for f in model._meta.fields]

            with open(file_path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(field_names)
                for obj in qs.iterator():
                    writer.writerow([getattr(obj, field) for field in field_names])

            csv_files.append((filename, file_path))

        # catalog：單一觀測項目 => 用 scientificName 欄位產生去重複名錄
        elif dl.mode == DownloadRequest.MODE_CATALOG:
            if len(obs_codes) != 1:
                raise ValueError("catalog 模式 items 只能包含 1 個項目")

            code = obs_codes[0]
            cfg = OBS_CONFIG[code]
            model = cfg["model"]

            field_names = [f.name for f in model._meta.fields]
            if "scientificName" not in field_names:
                raise ValueError(
                    f"{code} 的資料 model 沒有 scientificName 欄位，無法產生名錄"
                )

            names_qs = (
                model.objects.exclude(scientificName__isnull=True)
                .exclude(scientificName__exact="")
                .values_list("scientificName", flat=True)
                .distinct()
                .order_by("scientificName")
            )

            names = list(names_qs)
            if not names:
                raise ValueError(f"{code} 名錄為空，未產生任何 CSV 檔案")

            filename = f"{code}_CATALOG.csv"
            file_path = os.path.join(download_dir, filename)

            with open(file_path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(["scientificName"])
                for n in names:
                    writer.writerow([n])

            csv_files.append((filename, file_path))

        else:
            raise ValueError(f"未知 mode: {dl.mode}")

        if not csv_files:
            raise ValueError("符合條件的觀測資料為空，未產生任何 CSV 檔案")

        zip_filename = f"download_{dl.id}.zip"
        zip_path = os.path.join(download_dir, zip_filename)

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for filename, file_path in csv_files:
                zf.write(file_path, arcname=filename)

        for _, file_path in csv_files:
            try:
                os.remove(file_path)
            except OSError:
                pass

        dl.status = DownloadRequest.STATUS_DONE
        dl.zip_path = zip_path
        dl.finished_at = datetime.now()
        dl.error_message = ""
        dl.save(update_fields=["status", "zip_path", "finished_at", "error_message"])

        # 寄信
        try:
            site_base = settings.SITE_BASE_URL.rstrip("/")
            download_url = f"{site_base}{reverse('download-file', args=[dl.id])}"

            subject = "[臺灣長期社會生態核心觀測 阿里山站] 您的資料下載已準備完成"
            message = (
                f"{dl.first_name} 您好：\n\n"
                f"您申請的資料下載已經準備完成，請點擊以下連結下載檔案：\n\n"
                f"{download_url}\n\n"
                "請於期限（7天）內完成下載。\n\n"
                "此信件為系統自動寄出，請勿直接回覆。"
            )

            email = EmailMessage(
                subject,
                message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[dl.email],
            )
            email.send(fail_silently=False)

            dl.email_sent = True
            dl.email_error = ""
            dl.save(update_fields=["email_sent", "email_error"])

        except Exception as e:
            dl.email_sent = False
            dl.email_error = str(e)
            dl.save(update_fields=["email_sent", "email_error"])

    except Exception as e:
        dl.status = DownloadRequest.STATUS_FAILED
        dl.error_message = str(e)
        dl.finished_at = datetime.now()
        dl.save(update_fields=["status", "error_message", "finished_at"])
        raise


@shared_task
def cleanup_old_zips(days: int = 7):
    """
    刪除已完成且超過 N 天的 ZIP 檔案，並清空 zip_path。
    days 預設為 7 天
    """
    # 計算截止時間
    threshold = datetime.now() - timedelta(days=days)

    # 只找已完成且有 zip_path 的紀錄
    qs = DownloadRequest.objects.filter(
        status=DownloadRequest.STATUS_DONE,
        finished_at__lt=threshold,
    ).exclude(zip_path="")

    deleted_files = 0
    updated_rows = 0

    for dl in qs:
        zip_path = dl.zip_path
        if zip_path and os.path.exists(zip_path):
            try:
                os.remove(zip_path)
                deleted_files += 1
            except OSError:
                pass

        dl.zip_path = ""
        dl.status = DownloadRequest.STATUS_EXPIRED
        dl.save(update_fields=["zip_path", "status"])
        updated_rows += 1

    return {
        "deleted_files": deleted_files,
        "updated_rows": updated_rows,
        "threshold": threshold.isoformat(),
    }


@shared_task
def cache_village_population():
    latest_time = get_latest_time_list("village", query_type="summary")
    rows = get_population_data("village", latest_time, query_type="summary")

    payload = transform_population(rows)

    cache.set(
        segis_cache_key("village_population"),
        payload,
        timeout=None,  # 由下一次 celery 覆蓋
    )


@shared_task
def cache_village_dynamics():
    pop_time = get_latest_time_list("village", query_type="summary")
    idx_time = get_latest_time_list("village", query_type="index")
    dyn_time = get_latest_time_list("village", query_type="dynamics")

    population = get_population_data("village", pop_time, query_type="summary")
    index = get_population_data("village", idx_time, query_type="index")
    dynamics = get_population_data("village", dyn_time, query_type="dynamics")

    payload = transform_dynamics(
        population_rows=population,
        index_rows=index,
        dynamic_rows=dynamics,
    )

    cache.set(segis_cache_key("village_dynamics"), payload, timeout=None)


@shared_task
def cache_town_pyramid():
    latest_time = get_latest_time_list("town", query_type="pyramid")
    rows = get_population_data("town", latest_time, query_type="pyramid")

    cache.set(segis_cache_key("town_pyramid"), rows, timeout=None)


@shared_task
def cache_town_industry():
    ind_time = get_latest_time_list("town", query_type="industry")
    live_time = get_latest_time_list("town", query_type="livestock")

    industry = get_industry_data(ind_time, query_type="industry")
    livestock = get_industry_data(live_time, query_type="livestock")

    payload = transform_industry(
        industry_rows=industry,
        livestock_rows=livestock,
    )

    cache.set(segis_cache_key("town_industry"), payload, timeout=None)

def format_slack_text(
    report, site=None, observation_item=None, resource_name=None, task_id=None
):
    rid = report.get("resource_id", "(unknown)")
    fatal = report.get("fatal_errors") or []

    title_left = site or "(unknown site)"
    title_right = observation_item or "(unknown observation)"
    rn = resource_name or report.get("resource_name") or "(unknown)"

    lines = [
        f"{title_left}｜{title_right}",
        f"resource_name: {rn}",
        f"resource_id: {rid}",
        f"task_id: {task_id or '(unknown)'}",
        "",
        f"records_seen: {report.get('records_seen', 0)} / total: {report.get('total')}",
        f"inserted: {report.get('inserted', 0)}",
        f"updated: {report.get('updated', 0)}",
        f"skipped: {report.get('skipped', 0)}",
        f"row_errors: {report.get('row_errors', 0)}",
        f"row_warnings: {report.get('row_warnings', 0)}",
        f"fatal_errors: {len(fatal)}",
    ]

    # lines += format_slack_ipt_sync_lines(report) 
    # 之後有同步至 IPT 功能後才啟動

    if fatal:
        sample = "\n".join([str(x) for x in fatal[:3]])
        lines += ["", "⚠️ Fatal sample:", sample]

    body = "\n".join(lines)

    return f"*[Alishan]*\n\n匯入驗證結果\n```{body}```"

def to_taipei_time(dt_str):
    if not dt_str:
        return None

    dt = datetime.fromisoformat(dt_str)  # 解析 ISO 8601
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt, timezone.utc)

    taipei_tz = timezone.get_fixed_timezone(480)  # UTC+8
    return dt.astimezone(taipei_tz)


def parse_error_key(key):
    """
    將 'time.invalid_format' 拆成 ('time', 'invalid_format')
    若格式不符，全部當成 problem
    """
    if "." in key:
        field, problem = key.split(".", 1)
    else:
        field, problem = key, "unknown"
    return field, problem


def get_error_label(field, problem):
    return ERROR_FIELD_PROBLEM_LABELS.get(
        (field, problem), ERROR_PROBLEM_LABELS.get(problem, problem)
    )


def format_error_breakdown(report, max_items=10):
    breakdown = report.get("error_breakdown") or {}
    if not breakdown:
        return ""

    items = sorted(breakdown.items(), key=lambda kv: kv[1], reverse=True)[:max_items]

    lines = []
    lines.append("──────────────────────────")
    lines.append("⚠️ 匯入錯誤摘要")
    lines.append("──────────────────────────")
    lines.append(
        "本次資料匯入未能成功完成。\n"
        "請子計畫負責人依下列錯誤說明修正原始資料後，\n"
        "重新將修改完成的資料集上傳至 Depositar，系統將再自動排程處理。\n"
    )
    lines.append("【錯誤類型統計】")

    for key, count in items:
        field, problem = parse_error_key(key)
        lines.append(f"- 欄位：{field}")
        label = get_error_label(field, problem)
        lines.append(f"      問題：{label}")
        lines.append(f"      影響筆數：{count} 筆")

    lines.append("")
    return "\n".join(lines)


def format_fatal_hint(report):
    fatal_errors = report.get("fatal_errors") or []
    if not fatal_errors:
        return ""

    fe = fatal_errors[0] or {}
    code = fe.get("error", "")
    exc = fe.get("exception", "")

    if (
        code == "db_write_failed"
        and "bulk_update() objects must have a primary key set" in exc
    ):
        return (
            "──────────────────────────\n"
            "⚠️ 重要提醒：可能為 dataID 重複\n"
            "──────────────────────────\n"
            "系統在寫入資料庫時失敗。此狀況通常是資料中的 dataID（或唯一識別欄位）出現重複值，\n"
            "導致系統無法正確更新資料。\n\n"
            "dataID 重複可能發生在以下情況：\n"
            "1) 同一個資料集內部，存在重複的 dataID\n"
            "2) 本次上傳的資料，其 dataID 與站點中既有資料集的 dataID 發生重複\n\n"
        )

    return (
        "──────────────────────────\n"
        "⚠️ 系統錯誤提示\n"
        "──────────────────────────\n"
        "本次匯入過程發生系統錯誤，未完成寫入。\n"
    )


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def import_ckan_and_notify(
    self,
    package_name,
    resource_id,
    base_url,
    site=None,
    observation_item=None,
    resource_name=None,
    limit=100,
    notify_slack=True,
):
    adapter_cls = ADAPTERS.get(package_name)
    if not adapter_cls:
        raise ValueError("unknown_dataset: %s" % package_name)

    adapter = adapter_cls()
    report = import_ckan_resource(
        resource_id=resource_id,
        base_url=base_url,
        limit=limit,
        adapter=adapter,
    )

    report["celery_task_id"] = self.request.id

    if notify_slack:
        webhook = os.environ.get("SLACK_WEBHOOK_URL")
    else:
        webhook = None

    if webhook:
        try:
            text = format_slack_text(
                report,
                site=site,
                observation_item=observation_item,
                resource_name=resource_name,
                task_id=self.request.id,
            )
            requests.post(webhook, json={"text": text}, timeout=10)
        except Exception:
            pass

    return report

@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def send_import_slack(
    self,
    report,
    *,
    site=None,
    observation_item=None,
    resource_name=None,
):
    webhook = os.environ.get("SLACK_WEBHOOK_URL")
    if not webhook:
        return report

    text = format_slack_text(
        report,
        site=site,
        observation_item=observation_item,
        resource_name=resource_name,
        task_id=report.get("celery_task_id") or self.request.id,
    )
    requests.post(webhook, json={"text": text}, timeout=10)
    return report

@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def send_import_email(
    self,
    report,  # 接到 import_ckan_and_notify 的 return report
    *,
    to_emails,
    cc_emails=None,
    observation_item=None,
    resource_name=None,
    task_id=None,
):
    root_id = getattr(self.request, "root_id", None) or task_id
    if root_id:
        dedupe_key = f"import_email_sent:{root_id}"
        if not cache.add(dedupe_key, "1", timeout=60 * 60 * 24 * 7):
            return {"skipped": True, "reason": "duplicate"}

    if not to_emails:
        return {"skipped": True, "reason": "to_email_missing"}

    row_errors = report.get("row_errors", 0)
    row_warnings = report.get("row_warnings", 0)

    inserted = report.get("inserted", 0)
    updated = report.get("updated", 0)
    skipped = report.get("skipped", 0)

    records_seen = report.get("records_seen", 0)
    total = report.get("total", 0)

    started_at = report.get("started_at")
    finished_at = report.get("finished_at")

    started_at_tw = to_taipei_time(started_at)
    finished_at_tw = to_taipei_time(finished_at)

    started_at_str = (
        started_at_tw.strftime("%Y-%m-%d %H:%M:%S") if started_at_tw else "—"
    )
    finished_at_str = (
        finished_at_tw.strftime("%Y-%m-%d %H:%M:%S") if finished_at_tw else "—"
    )

    task_id_in_report = report.get("celery_task_id")

    error_section = format_error_breakdown(report)
    fatal_hint = format_fatal_hint(report)
    ipt_sync = report.get("ipt_sync") or {}
    ipt_sync_section = ""
    if ipt_sync and not ipt_sync.get("skipped"):
        occurrence_result = ipt_sync.get("occurrence_extension") or {}
        event_result = ipt_sync.get("event") or {}
        ipt_sync_section = (
            "\n"
            "──────────────────────────\n"
            "IPT 同步結果\n"
            "──────────────────────────\n"
            f"Event core 同步筆數：{event_result.get('synced_events', 0)}\n"
            f"Event core 新增/更新：{event_result.get('created', 0)} / {event_result.get('updated', 0)}\n\n"
            f"Occurrence extension 同步筆數：{occurrence_result.get('synced_occurrences', 0)}\n"
            f"Occurrence extension 新增/更新：{occurrence_result.get('created', 0)} / {occurrence_result.get('updated', 0)}\n"
            "\n"
            "後續請至 IPT 資料集管理頁面確認資料集內容。\n"
            "進入該資料集後，可於 Source Data 區塊點擊 Save，讓 IPT 重新讀取並套用最新同步資料；\n"
            "確認資料無誤後，再至 Publication 區塊發布新版資料集。\n"
        )

    fatal_errors = report.get("fatal_errors") or []

    status_tag = "成功"
    if fatal_errors:
        status_tag = "失敗（系統寫入錯誤）"
    elif row_errors and (inserted == 0 and updated == 0):
        status_tag = "失敗（資料格式錯誤）"
    elif row_errors:
        status_tag = "完成但有錯誤"
    elif row_warnings:
        status_tag = "完成但有警告"

    if status_tag == "成功":
        subject = (
            f"臺灣長期社會生態核心觀測站 阿里山站 | {resource_name} 資料已匯入至站點網站"
        )
    else:
        subject = f"臺灣長期社會生態核心觀測站 阿里山站 | {resource_name} 資料匯入至站點網站 {status_tag}"

    if fatal_errors:
        intro = (
            f"您好，\n\n"
            f"您所負責的「{observation_item}」子計畫中，\n"
            f"資料集「{resource_name}」匯入至網站資料庫時發生錯誤，未完成寫入。\n\n"
            f"如需確認站點目前資料狀態，可至下列網址查看：\n"
            f"https://ltsertwalishan.org/\n\n"
        )
    else:
        intro = (
            f"您好，\n\n"
            f"您所負責的「{observation_item}」子計畫中，\n"
            f"資料集「{resource_name}」已匯入至網站資料庫中。\n\n"
            f"最新資料可至下列網址查看：\n"
            f"https://ltsertwalishan.org/\n\n"
        )

    body = intro + (
        f"──────────────────────────\n"
        f"本次資料匯入統計摘要\n"
        f"──────────────────────────\n"
        f"插入筆數：{inserted}\n"
        f"更新筆數：{updated}\n"
        f"略過筆數：{skipped}\n"
        f"錯誤筆數：{row_errors}\n"
        f"警告筆數：{row_warnings}\n\n"
        f"資料總筆數：{total}\n"
        f"實際處理筆數：{records_seen}\n\n"
        f"匯入開始時間：{started_at_str}\n"
        f"匯入完成時間：{finished_at_str}\n\n"
        f"【資料狀態說明】\n"
        f"插入筆數：成功新增至資料庫中的資料筆數\n"
        f"更新筆數：已存在於資料庫中，且部分內容被更新的資料筆數\n"
        f"略過筆數：資料已存在於資料庫，且內容無異動而未進行新增或更新的筆數\n"
        f"錯誤筆數：因格式或內容錯誤而無法匯入，且未寫入資料庫的資料筆數\n"
        f"警告筆數：資料可成功匯入，但內容可能需人工確認的資料筆數\n"
        f"{ipt_sync_section}"
        f"{fatal_hint}"
        f"{error_section}"
        f"\n"
        f"──────────────────────────\n"
        f"本信件為系統自動發送，若有任何疑問請直接回覆信件。\n"
        f"task ID: {task_id_in_report}\n"
    )

    email = EmailMessage(
        subject=subject,
        body=body,
        from_email=settings.EMAIL_HOST_USER,
        to=to_emails,
        cc=cc_emails,
    )
    email.send(fail_silently=False)

    return {"sent": True}
