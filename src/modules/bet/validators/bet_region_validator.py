from datetime import date

from src.modules.schedule.services.region_schedule_service import (
    validate_region_for_date,
)


def validate_bet_region(region: str, bet_date: date):
    """
    校验下注区域是否允许在该日期下注
    """

    result = validate_region_for_date(region, bet_date)

    if not result.is_allowed:
        return False, result

    return True, result