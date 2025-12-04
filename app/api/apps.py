from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "api"

    def ready(self):
        """
        Django 啟動時會呼叫這裡，我們在這裡綁 signals。
        """
        from django.db.models.signals import post_save, post_delete

        from .models import Location
        from .obs_config import OBS_CONFIG
        from .tasks import (
            rebuild_location_map_filter_cache,
            rebuild_location_map_list_cache,
        )

        # 會影響首頁地圖/下拉的所有 models：
        # Location + OBS_CONFIG 裡面的每一個觀測 model
        tracked_models = [Location] + [cfg["model"] for cfg in OBS_CONFIG.values()]

        def _trigger_cache_rebuild(sender, **kwargs):
            """
            只要有相關 model 被新增/更新/刪除，就丟 Celery 去重建 cache。
            這裡不清 cache，讓舊資料繼續用，重建完成後會直接覆蓋。
            """
            rebuild_location_map_filter_cache.delay()
            rebuild_location_map_list_cache.delay()

        for model in tracked_models:
            post_save.connect(
                _trigger_cache_rebuild,
                sender=model,
                dispatch_uid=f"{model.__name__}_save_cache_rebuild",
            )
            post_delete.connect(
                _trigger_cache_rebuild,
                sender=model,
                dispatch_uid=f"{model.__name__}_delete_cache_rebuild",
            )
