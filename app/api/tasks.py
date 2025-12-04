from celery import shared_task
from django.core.cache import cache

from .utils.cache_keys import location_map_list_key, location_map_filter_key
from .models import Location
from .serializers import LocationMapSerializer
from .obs_config import OBS_CONFIG
from collections import defaultdict


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
