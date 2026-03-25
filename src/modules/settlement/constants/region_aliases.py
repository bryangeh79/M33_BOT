"""
Region alias mapping

用于将用户输入的区域代码（bt / vt / bl 等）
转换为数据库中的标准 sub_region_code
"""

REGION_ALIAS_MAP = {
    # ===== Shared / explicit full names =====
    "bentre": "BENTRE",
    "vungtau": "VUNGTAU",
    "baclieu": "BACLIEU",
    "camau": "CAMAU",
    "cantho": "CANTHO",
    "dongnai": "DONGNAI",
    "dongthap": "DONGTHAP",
    "haugiang": "HAUGIANG",
    "kiengiang": "KIENGIANG",
    "longan": "LONGAN",
    "soctrang": "SOCTRANG",
    "tiengiang": "TIENGIANG",
    "tayninh": "TAYNINH",
    "travinh": "TRAVINH",
    "vinhlong": "VINHLONG",
    "danang": "DANANG",
    "quangnam": "QUANGNAM",
    "quangbinh": "QUANGBINH",
    "quangtri": "QUANGTRI",
    "binhdinh": "BINHDINH",
    "phuyen": "PHUYEN",
    "khanhhoa": "KHANHHOA",
    "dalat": "DALAT",
    "daknong": "DAKNONG",
    "gialai": "GIALAI",
    "kontum": "KONTUM",
    "hue": "HUE",
    "mb": "MB",
}

MN_REGION_ALIAS_MAP = {
    "bt": "BENTRE",
    "vt": "VUNGTAU",
    "bl": "BACLIEU",
    "cm": "CAMAU",
    "ct": "CANTHO",
    "dn": "DONGNAI",
    "dnai": "DONGNAI",
    "dt": "DONGTHAP",
    "hg": "HAUGIANG",
    "kg": "KIENGIANG",
    "la": "LONGAN",
    "st": "SOCTRANG",
    "tg": "TIENGIANG",
    "tn": "TAYNINH",
    "tv": "TRAVINH",
    "vl": "VINHLONG",
}

MT_REGION_ALIAS_MAP = {
    "dn": "DANANG",
    "dna": "DANANG",
    "qna": "QUANGNAM",
    "qbi": "QUANGBINH",
    "qtr": "QUANGTRI",
    "bdi": "BINHDINH",
    "py": "PHUYEN",
    "kh": "KHANHHOA",
    "dla": "DALAT",
    "dno": "DAKNONG",
    "gl": "GIALAI",
    "kt": "KONTUM",
    "tth": "HUE",
}


def normalize_region_alias(region_code: str, region_group: str | None = None) -> str:
    if not region_code:
        return ""

    key = region_code.strip().lower()
    normalized_group = str(region_group or "").strip().upper()

    if normalized_group == "MN" and key in MN_REGION_ALIAS_MAP:
        return MN_REGION_ALIAS_MAP[key]

    if normalized_group == "MT" and key in MT_REGION_ALIAS_MAP:
        return MT_REGION_ALIAS_MAP[key]

    return REGION_ALIAS_MAP.get(key, region_code.strip().upper())
