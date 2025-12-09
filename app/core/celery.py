import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
app = Celery("core")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "cleanup-old-download-zips": {
        "task": "api.tasks.cleanup_old_zips",
        "schedule": crontab(hour=3, minute=0),  # 每天凌晨 3 點跑一次
        "args": (7,),  # 保留 7 天，超過就刪
    },
}
