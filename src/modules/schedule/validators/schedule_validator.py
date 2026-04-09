from datetime import date

from src.modules.schedule.services.region_schedule_service import is_region_allowed
from src.modules.schedule.constants.region_schedule_map import get_allowed_regions


class ScheduleValidationResult:

    def __init__(
        self,
        is_allowed: bool,
        requested_region: str,
        region_group: str,
        target_date: date,
        allowed_regions: list,
        reason: str | None = None,
    ):
        self.is_allowed = is_allowed
        self.requested_region = requested_region
        self.region_group = region_group
        self.target_date = target_date
        self.allowed_regions = allowed_regions
        self.reason = reason


def validate_schedule(
    region_group: str,
    region_code: str,
    target_date: date,
) -> ScheduleValidationResult:
    """
    Validate whether a region is allowed to accept bets on a given date.
    """

    allowed_regions = get_allowed_regions(target_date, region_group)

    allowed = is_region_allowed(region_group, region_code, target_date)

    if allowed:
        return ScheduleValidationResult(
            is_allowed=True,
            requested_region=region_code,
            region_group=region_group,
            target_date=target_date,
            allowed_regions=allowed_regions,
        )

    return ScheduleValidationResult(
        is_allowed=False,
        requested_region=region_code,
        region_group=region_group,
        target_date=target_date,
        allowed_regions=allowed_regions,
        reason="REGION_NOT_OPEN_TODAY",
    )