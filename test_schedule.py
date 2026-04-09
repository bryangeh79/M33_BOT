from datetime import date

from src.modules.schedule.services.region_schedule_service import (
    get_allowed_regions_for_date,
    validate_region_for_date,
)

today = date.today()

print("Today:", today)

allowed = get_allowed_regions_for_date(today)
print("Allowed regions:", allowed)

result1 = validate_region_for_date("MN", today)
print("Test MN:", result1)

result2 = validate_region_for_date("MB", today)
print("Test MB:", result2)