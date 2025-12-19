from collections import defaultdict

VID_TO_VILLNAME = {
    "10010180-001": "中山村",
    "10010180-005": "來吉村",
    "10010180-007": "達邦村",
    "10010180-008": "樂野村",
    "10010180-009": "里佳村",
    "10010180-010": "山美村",
    "10010180-011": "新美村",
    "10010180-012": "茶山村",
    "10010160-009": "公田村",
}

FIELD_LABEL = {
    "P_CNT": "人口數",
    "M_F_RAT": "性別比",
    "DEPENDENCY_RAT": "扶養比",
    "A65UP_A15A64_RAT": "扶老比",
    "A65_A0A14_RAT": "老化指數",
    "NATURE_INC_CNT": "自然增加人數",
    "SOCIAL_INC_CNT": "社會增加人數",
}

METRICS = [
    "P_CNT",
    "M_F_RAT",
    "DEPENDENCY_RAT",
    "A65UP_A15A64_RAT",
    "A65_A0A14_RAT",
    "NATURE_INC_CNT",
    "SOCIAL_INC_CNT",
]

AGE_BUCKETS = [
    ("0-4歲", "A0A4_M_CNT", "A0A4_F_CNT"),
    ("5-9歲", "A5A9_M_CNT", "A5A9_F_CNT"),
    ("10-14歲", "A10A14_M_CNT", "A10A14_F_CNT"),
    ("15-19歲", "A15A19_M_CNT", "A15A19_F_CNT"),
    ("20-24歲", "A20A24_M_CNT", "A20A24_F_CNT"),
    ("25-29歲", "A25A29_M_CNT", "A25A29_F_CNT"),
    ("30-34歲", "A30A34_M_CNT", "A30A34_F_CNT"),
    ("35-39歲", "A35A39_M_CNT", "A35A39_F_CNT"),
    ("40-44歲", "A40A44_M_CNT", "A40A44_F_CNT"),
    ("45-49歲", "A45A49_M_CNT", "A45A49_F_CNT"),
    ("50-54歲", "A50A54_M_CNT", "A50A54_F_CNT"),
    ("55-59歲", "A55A59_M_CNT", "A55A59_F_CNT"),
    ("60-64歲", "A60A64_M_CNT", "A60A64_F_CNT"),
    ("65-69歲", "A65A69_M_CNT", "A65A69_F_CNT"),
    ("70-74歲", "A70A74_M_CNT", "A70A74_F_CNT"),
    ("75-79歲", "A75A79_M_CNT", "A75A79_F_CNT"),
    ("80-84歲", "A80A84_M_CNT", "A80A84_F_CNT"),
    ("85-89歲", "A85A89_M_CNT", "A85A89_F_CNT"),
    ("90-94歲", "A90A94_M_CNT", "A90A94_F_CNT"),
    ("95-99歲", "A95A99_M_CNT", "A95A99_F_CNT"),
    ("100歲以上", "A100UP_5_M_CNT", "A100UP_5_F_CNT"),
]

FRONTEND_FIELD_MAP = {
    "0-4歲人口數": "A0A4_CNT",
    "0-4歲男性人口數": "A0A4_M_CNT",
    "0-4歲女性人口數": "A0A4_F_CNT",
    "5-9歲人口數": "A5A9_CNT",
    "5-9歲男性人口數": "A5A9_M_CNT",
    "5-9歲女性人口數": "A5A9_F_CNT",
    "10-14歲人口數": "A10A14_CNT",
    "10-14歲男性人口數": "A10A14_M_CNT",
    "10-14歲女性人口數": "A10A14_F_CNT",
    "15-19歲人口數": "A15A19_CNT",
    "15-19歲男性人口數": "A15A19_M_CNT",
    "15-19歲女性人口數": "A15A19_F_CNT",
    "20-24歲人口數": "A20A24_CNT",
    "20-24歲男性人口數": "A20A24_M_CNT",
    "20-24歲女性人口數": "A20A24_F_CNT",
    "25-29歲人口數": "A25A29_CNT",
    "25-29歲男性人口數": "A25A29_M_CNT",
    "25-29歲女性人口數": "A25A29_F_CNT",
    "30-34歲人口數": "A30A34_CNT",
    "30-34歲男性人口數": "A30A34_M_CNT",
    "30-34歲女性人口數": "A30A34_F_CNT",
    "35-39歲人口數": "A35A39_CNT",
    "35-39歲男性人口數": "A35A39_M_CNT",
    "35-39歲女性人口數": "A35A39_F_CNT",
    "40-44歲人口數": "A40A44_CNT",
    "40-44歲男性人口數": "A40A44_M_CNT",
    "40-44歲女性人口數": "A40A44_F_CNT",
    "45-49歲人口數": "A45A49_CNT",
    "45-49歲男性人口數": "A45A49_M_CNT",
    "45-49歲女性人口數": "A45A49_F_CNT",
    "50-54歲人口數": "A50A54_CNT",
    "50-54歲男性人口數": "A50A54_M_CNT",
    "50-54歲女性人口數": "A50A54_F_CNT",
    "55-59歲人口數": "A55A59_CNT",
    "55-59歲男性人口數": "A55A59_M_CNT",
    "55-59歲女性人口數": "A55A59_F_CNT",
    "60-64歲人口數": "A60A64_CNT",
    "60-64歲男性人口數": "A60A64_M_CNT",
    "60-64歲女性人口數": "A60A64_F_CNT",
    "65-69歲人口數": "A65A69_CNT",
    "65-69歲男性人口數": "A65A69_M_CNT",
    "65-69歲女性人口數": "A65A69_F_CNT",
    "70-74歲人口數": "A70A74_CNT",
    "70-74歲男性人口數": "A70A74_M_CNT",
    "70-74歲女性人口數": "A70A74_F_CNT",
    "75-79歲人口數": "A75A79_CNT",
    "75-79歲男性人口數": "A75A79_M_CNT",
    "75-79歲女性人口數": "A75A79_F_CNT",
    "80-84歲人口數": "A80A84_CNT",
    "80-84歲男性人口數": "A80A84_M_CNT",
    "80-84歲女性人口數": "A80A84_F_CNT",
    "85-89歲人口數": "A85A89_CNT",
    "85-89歲男性人口數": "A85A89_M_CNT",
    "85-89歲女性人口數": "A85A89_F_CNT",
    "90-94歲人口數": "A90A94_CNT",
    "90-94歲男性人口數": "A90A94_M_CNT",
    "90-94歲女性人口數": "A90A94_F_CNT",
    "95-99歲人口數": "A95A99_CNT",
    "95-99歲男性人口數": "A95A99_M_CNT",
    "95-99歲女性人口數": "A95A99_F_CNT",
    "100歲以上人口數": "A100UP_5_CNT",
    "100歲以上男性人口數": "A100UP_5_M_CNT",
    "100歲以上女性人口數": "A100UP_5_F_CNT",
    "資料時間": "INFO_TIME",
}

INDUSTRY_SERIES = [
    ("C1_A_CNT", "農、林、漁、牧業"),
    ("C1_B_CNT", "礦業及土石採取業"),
    ("C1_C_CNT", "製造業"),
    ("C1_D_CNT", "電力及燃氣供應業"),
    ("C1_E_CNT", "用水供應及污染整治業"),
    ("C1_F_CNT", "營造業"),
    ("C1_G_CNT", "批發及零售業"),
    ("C1_H_CNT", "運輸及倉儲業"),
    ("C1_I_CNT", "住宿及餐飲業"),
    ("C1_J_CNT", "資訊及通訊傳播業"),
    ("C1_K_CNT", "金融及保險業"),
    ("C1_L_CNT", "不動產業"),
    ("C1_M_CNT", "專業、科學及技術服務業"),
    ("C1_N_CNT", "支援服務業"),
    ("C1_O_CNT", "公共行政及國防；強制性社會安全"),
    ("C1_P_CNT", "教育服務業"),
    ("C1_Q_CNT", "醫療保健及社會工作服務業"),
    ("C1_R_CNT", "藝術、娛樂及休閒服務業"),
    ("C1_S_CNT", "其他服務業"),
]

LIVESTOCK_SERIES = [
    ("COLUMN1", "現有豬頭數"),
    ("COLUMN2", "現有乳牛頭數"),
    ("COLUMN3", "現有羊頭數"),
]


def _parse_info_time(info_time):
    """
    支援兩種資料：
        - 年底人口/指數：'113Y12M' -> (113, 12)
        - 動態資料：     '113Y4S'  -> (113, 4)
    回傳 (roc_year, sub_period) 用來挑同年最新一期
    """
    if not info_time or "Y" not in info_time:
        return None, 0

    try:
        y_part, rest = info_time.split("Y", 1)
        roc_year = int(y_part)

        if rest.endswith("M"):
            sub = int(rest[:-1])  # 12
        elif rest.endswith("S"):
            sub = int(rest[:-1])  # 4
        else:
            sub = 0

        return roc_year, sub
    except Exception:
        return None, 0


def _to_int(v):
    try:
        return int(round(float(v)))
    except Exception:
        return 0


def _to_float(v):
    if v is None:
        return None
    try:
        return float(v)
    except Exception:
        return None


def _iter_latest_rows_by_year(rows, *, with_village=False):
    """
    回傳 iterable：
      - with_village=False: (ad_year, row)
      - with_village=True : (ad_year, vill_name, row)
    """
    best = {}  # key -> (sub, row)

    for r in rows or []:
        info_time = str(r.get("INFO_TIME", "")).strip()
        if not info_time:
            continue

        roc, sub = _parse_info_time(info_time)
        if not roc:
            continue

        ad_year = roc + 1911
        sub = int(sub or 0)

        if with_village:
            v_id = str(r.get("V_ID", "")).strip()
            vill = VID_TO_VILLNAME.get(v_id)
            if not vill:
                continue
            key = (ad_year, vill)
        else:
            key = ad_year

        if key not in best or sub > best[key][0]:
            best[key] = (sub, r)

    for key, (_sub, row) in best.items():
        if with_village:
            y, v = key
            yield y, v, row
        else:
            yield key, row


def _pick_latest_row_by_year(rows):
    return {y: row for y, row in _iter_latest_rows_by_year(rows)}


def _pick_latest_by_year(rows, keys):
    out = {}
    for y, vill, row in _iter_latest_rows_by_year(rows, with_village=True):
        values = {
            k: _to_float(row.get(k)) for k in keys if _to_float(row.get(k)) is not None
        }
        if values:
            out[(y, vill)] = values
    return out


def _series_data_by_year(years, year_to_row, key):
    out = []
    for y in years:
        row = year_to_row.get(y)
        out.append(_to_float(row.get(key)) if row else None)
    return out


def transform_population(rows):
    """
    {
        years: [...],
        data_by_year: {
            "113Y12M": { "中山村": 372, "來吉村": 344 }
        }
    }
    """

    data_by_year = defaultdict(dict)
    latest = {}

    # 轉換成前端需要的格式
    for r in rows:
        info_time = str(r.get("INFO_TIME", "")).strip()
        v_id = str(r.get("V_ID", "")).strip()
        if not info_time or not v_id:
            continue

        vill_name = VID_TO_VILLNAME.get(v_id)
        if not vill_name:
            continue

        roc_y, month = _parse_info_time(info_time)
        if roc_y <= 0:
            continue
        ad_year = roc_y + 1911

        try:
            population = int(float(r.get("P_CNT", 0)))
        except Exception:
            population = 0

        key = (ad_year, vill_name)
        prev = latest.get(key)
        if prev is None or month >= prev[0]:
            latest[key] = (month, population)

    # 組回 data_by_year
    for (ad_year, vill_name), (_month, population) in latest.items():
        data_by_year[str(ad_year)][vill_name] = population

    # years 照年份排序
    years = sorted({int(y) for y in data_by_year.keys()})

    return {
        "years": years,
        "data_by_year": data_by_year,
    }


def transform_dynamics(
    population_rows,
    index_rows,
    dynamic_rows,
):
    """
    {
        "years": [2020, 2021, ...],
        "metrics": {
            "M_F_RAT": {"label": "...", "series": {"中山村":[...], ...}},
            ...
        }
    }。
    """

    pop_map = _pick_latest_by_year(population_rows, ["P_CNT"])
    idx_map = _pick_latest_by_year(
        index_rows,
        ["M_F_RAT", "DEPENDENCY_RAT", "A65UP_A15A64_RAT", "A65_A0A14_RAT"],
    )

    dyn_cnt_map = _pick_latest_by_year(
        dynamic_rows, ["NATURE_INC_CNT", "SOCIAL_INC_CNT"]
    )

    years_set = set()
    villages_set = set()

    for y, v in set(pop_map) | set(idx_map) | set(dyn_cnt_map):
        years_set.add(y)
        villages_set.add(v)

    years = sorted(years_set)
    villages = sorted(villages_set)

    year_idx = {y: i for i, y in enumerate(years)}
    n = len(years)

    metrics = {}
    for m in METRICS:
        metrics[m] = {
            "label": FIELD_LABEL.get(m, m),
            "series": {vill: [None] * n for vill in villages},
        }

    for (y, vill), d in pop_map.items():
        metrics["P_CNT"]["series"][vill][year_idx[y]] = d.get("P_CNT")

    for (y, vill), d in idx_map.items():
        for k in ("M_F_RAT", "DEPENDENCY_RAT", "A65UP_A15A64_RAT", "A65_A0A14_RAT"):
            if k in d:
                metrics[k]["series"][vill][year_idx[y]] = d[k]

    for (y, vill), d in dyn_cnt_map.items():
        if "NATURE_INC_CNT" in d:
            metrics["NATURE_INC_CNT"]["series"][vill][year_idx[y]] = d["NATURE_INC_CNT"]
        if "SOCIAL_INC_CNT" in d:
            metrics["SOCIAL_INC_CNT"]["series"][vill][year_idx[y]] = d["SOCIAL_INC_CNT"]

    return {
        "years": years,
        "metrics": metrics,
    }


def transform_pyramid(row_data_list, selected_year=None):
    """
    {
        "years": [2011, 2012, ...],
        "selected_year": 2011,
        "chart": {"xAxis":[...], "male":[...], "female":[...]},
    }
    """

    by_roc_year = defaultdict(list)
    year_latest_sub = {}

    for r in row_data_list or []:
        info_time = str(r.get("INFO_TIME", "")).strip()
        roc_year, sub = _parse_info_time(info_time)
        if not roc_year:
            continue

        roc_year = int(roc_year)
        sub = int(sub)

        by_roc_year[roc_year].append(r)
        if roc_year not in year_latest_sub or sub > year_latest_sub[roc_year]:
            year_latest_sub[roc_year] = sub

    if not by_roc_year:
        return {
            "years": [],
            "selected_year": None,
            "chart": {"xAxis": [], "male": [], "female": []},
        }

    # years 下拉選單民國年份轉成西元年
    years = sorted([roc + 1911 for roc in by_roc_year.keys()])

    # selected_year 沒給就用最新年
    selected_year = int(selected_year) if selected_year else years[-1]
    selected_roc = selected_year - 1911

    rows_same_year = by_roc_year.get(selected_roc, [])
    if not rows_same_year:
        # 使用者選了沒有的年：回 years + 空圖
        return {
            "years": years,
            "selected_year": selected_year,
            "chart": {"xAxis": [], "male": [], "female": []},
        }

    # 同一年取最新一期
    latest_sub = year_latest_sub[selected_roc]

    # 只取該年最新一期的 rows，加總成一筆圖表
    target_rows = []
    info_time_keep = None
    for r in rows_same_year:
        it = str(r.get("INFO_TIME", "")).strip()
        roc, sub = _parse_info_time(it)
        if int(roc) == selected_roc and int(sub) == latest_sub:
            target_rows.append(r)
            info_time_keep = info_time_keep or it

    # 加總
    x_axis = [label for (label, _, _) in AGE_BUCKETS]
    male = []
    female = []

    for _, m_key, f_key in AGE_BUCKETS:
        male.append(sum(_to_int(r.get(m_key, 0)) for r in target_rows))
        female.append(sum(_to_int(r.get(f_key, 0)) for r in target_rows))

    return {
        "years": years,  # ✅ 下拉用：number[]
        "selected_year": selected_year,  # ✅ 西元年 int
        "chart": {"xAxis": x_axis, "male": male, "female": female},
    }


def transform_industry(industry_rows, livestock_rows):
    ind_year_row = _pick_latest_row_by_year(industry_rows)
    live_year_row = _pick_latest_row_by_year(livestock_rows)

    years = sorted(set(ind_year_row.keys()) | set(live_year_row.keys()))

    charts = {
        "industry": {
            "title": "工商業家數（按產業別）",
            "series": [
                {
                    "key": key,
                    "name": name,
                    "data": _series_data_by_year(years, ind_year_row, key),
                }
                for key, name in INDUSTRY_SERIES
            ],
        },
        "livestock": {
            "title": "畜牧現有頭數",
            "series": [
                {
                    "key": key,
                    "name": name,
                    "data": _series_data_by_year(years, live_year_row, key),
                }
                for key, name in LIVESTOCK_SERIES
            ],
        },
    }

    return {"years": years, "charts": charts}
