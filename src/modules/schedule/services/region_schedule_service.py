from datetime import date

from src.modules.schedule.constants.region_schedule_map import get_allowed_regions


def is_region_allowed(region_group: str, region_code: str, target_date: date) -> bool:
    """
    Check whether a region_code is allowed for the given region_group on target_date.

    Example:
        region_group = "MN"
        region_code = "tp"
        target_date = 2026-03-16 (Monday)

        -> True
    """
    allowed_regions = get_allowed_regions(target_date, region_group)

    return str(region_code).lower() in allowed_regions


def get_schedule_info(region_group: str, target_date: date) -> dict:
    """
    Return schedule info for display / debugging / validation.
    """
    allowed_regions = get_allowed_regions(target_date, region_group)

    return {
        "region_group": region_group.upper(),
        "target_date": target_date.isoformat(),
        "allowed_regions": allowed_regions,
    }