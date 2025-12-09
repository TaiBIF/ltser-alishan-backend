import os
import csv
import io
import zipfile
from collections import defaultdict
from datetime import datetime, timedelta

from celery import shared_task
from django.core.cache import cache
from django.conf import settings
from django.core.mail import EmailMessage
from django.urls import reverse

from .utils.cache_keys import location_map_list_key, location_map_filter_key
from .models import Location, DownloadRequest
from .serializers import LocationMapSerializer
from .obs_config import OBS_CONFIG


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
def generate_download_zip(download_request_id: int):
    dl = DownloadRequest.objects.get(id=download_request_id)

    # 避免被重複處理
    if dl.status not in [DownloadRequest.STATUS_PENDING, DownloadRequest.STATUS_FAILED]:
        return

    dl.status = DownloadRequest.STATUS_PROCESSING
    dl.save(update_fields=["status"])

    try:
        # 1. 把前端的 label 轉成 code
        obs_label_to_code = {cfg["label"]: code for code, cfg in OBS_CONFIG.items()}

        requested_labels = dl.items  # ["植物物候", "氣象觀測"]
        # 可以允許前端直接傳 code，所以有兩種 mapping
        obs_codes = []
        for item in requested_labels:
            if item in OBS_CONFIG:  # 直接是 code
                obs_codes.append(item)
            elif item in obs_label_to_code:  # 中文 label
                obs_codes.append(obs_label_to_code[item])

        # 去掉不存在的的觀測項目
        obs_codes = [c for c in obs_codes if c in OBS_CONFIG]

        if not obs_codes:
            raise ValueError("沒有有效的觀測項目代碼可供匯出")

        # 2. 準備輸出目錄
        base_dir = getattr(settings, "MEDIA_ROOT", None)
        if not base_dir:
            raise ValueError("MEDIA_ROOT 尚未設定")

        download_dir = os.path.join(base_dir, "downloads", str(dl.id))
        os.makedirs(download_dir, exist_ok=True)

        # 3. 對每一個觀測項目輸出一個 CSV
        csv_files = []

        for code in obs_codes:
            cfg = OBS_CONFIG[code]
            model = cfg["model"]
            date_field = cfg["date_field"]

            qs = model.objects.filter(locationID=dl.location_id)
            qs = qs.filter(**{f"{date_field}__year": dl.year})

            if not qs.exists():
                # 沒資料就跳過，不生成檔案
                continue

            # 檔名，例如 plantphenology_2023_SIM.csv
            filename = f"{code}_{dl.year}_{dl.location_id}.csv"
            file_path = os.path.join(download_dir, filename)

            # 取得所有普通欄位輸出
            field_names = [f.name for f in model._meta.fields]

            with open(file_path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                # 寫欄位名稱
                writer.writerow(field_names)
                # 寫每筆資料
                for obj in qs:
                    row = [getattr(obj, field) for field in field_names]
                    writer.writerow(row)

            csv_files.append((filename, file_path))

        if not csv_files:
            raise ValueError("符合條件的觀測資料為空，未產生任何 CSV 檔案")

        # 4. 壓縮成一個 zip
        zip_filename = f"download_{dl.id}.zip"
        zip_path = os.path.join(download_dir, zip_filename)

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for filename, file_path in csv_files:
                # 第二個參數是壓縮檔內的檔名
                zf.write(file_path, arcname=filename)

        # 壓縮完成後，刪掉所有 CSV，只保留 zip
        for _, file_path in csv_files:
            try:
                os.remove(file_path)
            except OSError:
                pass

        # 5. 更新 DownloadRequest 狀態與 zip 路徑
        dl.status = DownloadRequest.STATUS_DONE
        dl.zip_path = zip_path
        dl.finished_at = datetime.now()
        dl.error_message = ""
        dl.save(update_fields=["status", "zip_path", "finished_at", "error_message"])

        # 6. 寄信給申請者
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

            from_email = settings.DEFAULT_FROM_EMAIL
            email = EmailMessage(
                subject,
                message,
                from_email=from_email,
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
