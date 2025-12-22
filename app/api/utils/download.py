from ..obs_config import OBS_CONFIG


def build_obs_maps():
    label_to_code = {cfg["label"]: code for code, cfg in OBS_CONFIG.items()}
    code_to_label = {code: cfg["label"] for code, cfg in OBS_CONFIG.items()}
    return label_to_code, code_to_label


def normalize_items_to_labels(items):
    if not isinstance(items, list) or not items:
        return []

    label_to_code, code_to_label = build_obs_maps()

    normalized = []
    for x in items:
        if not isinstance(x, str):
            continue
        x = x.strip()
        if not x:
            continue

        # 前端傳 code
        if x in code_to_label:
            normalized.append(code_to_label[x])
            continue

        # 前端傳 label
        if x in label_to_code:
            normalized.append(x)
            continue

        # 不認得就跳過
        continue

    # 去重複保序
    return list(dict.fromkeys(normalized))
