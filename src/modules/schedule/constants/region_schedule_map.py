from datetime import date


"""
Vietnam lottery weekly schedule.

Structure:

DAY_OF_WEEK
    ├ MN -> southern provinces
    ├ MT -> central provinces
    └ MB -> northern lottery
"""

REGION_SCHEDULE_MAP = {
    "monday": {
        "MN": ["tp", "dt", "cm"],
        "MT": ["py", "tth"],
        "MB": ["mb"],
    },
    "tuesday": {
        "MN": ["bt", "vt", "bl"],
        "MT": ["dla", "qna"],
        "MB": ["mb"],
    },
    "wednesday": {
        "MN": ["dn", "ct", "st"],
        "MT": ["kh", "dna"],
        "MB": ["mb"],
    },
    "thursday": {
        "MN": ["tn", "ag", "bth"],
        "MT": ["bdi", "qtr", "qbi"],
        "MB": ["mb"],
    },
    "friday": {
        "MN": ["bd", "tv", "vl"],
        "MT": ["gl", "nth"],
        "MB": ["mb"],
    },
    "saturday": {
        "MN": ["tp", "la", "bp", "hg"],
        "MT": ["dna", "qng", "dno"],  # dna = Da Nang, dno = Dak Nong
        "MB": ["mb"],
    },
    "sunday": {
        "MN": ["tg", "kg", "dl"],
        "MT": ["kt", "kh"],
        "MB": ["mb"],
    },
}


def get_weekday_key(target_date: date) -> str:
    """
    Convert date -> weekday string

    Example:
        2026-03-16 -> monday
    """
    return target_date.strftime("%A").lower()


def get_allowed_regions(target_date: date, region_group: str):
    """
    Return allowed region codes for given date and region group.
    """

    weekday = get_weekday_key(target_date)

    day_schedule = REGION_SCHEDULE_MAP.get(weekday, {})

    return day_schedule.get(region_group.upper(), [])
