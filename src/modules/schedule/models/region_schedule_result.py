from dataclasses import dataclass, field
from typing import List


@dataclass
class RegionScheduleValidationResult:
    is_allowed: bool
    requested_region: str
    target_date: str
    allowed_regions: List[str] = field(default_factory=list)
    reason: str = ""