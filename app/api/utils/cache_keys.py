def location_map_list_key(year: str | None, item: str | None) -> str:
    return f"location_map_list:{year or 'all'}:{item or 'all'}"


def location_map_filter_key() -> str:
    return "location_map_filter"
