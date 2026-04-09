from collections import defaultdict
from decimal import Decimal
from typing import Any

from src.modules.report.constants.report_constants import (
    REPORT_BET_TYPE_ORDER,
    REPORT_REGION_GROUPS,
)
from src.modules.report.helpers.report_normalizer import ReportNormalizer
from src.modules.report.repositories.report_repository import ReportRepository


class NumberDetailReportService:
    def __init__(
        self,
        repository: ReportRepository | None = None,
        normalizer: ReportNormalizer | None = None,
    ):
        self.repository = repository or ReportRepository()
        self.normalizer = normalizer or ReportNormalizer()

    def generate_report(self, target_date: str) -> dict[str, Any]:
        rows = self.repository.get_number_detail_rows(target_date)

        aggregated: dict[str, dict[str, dict[tuple[str, str], Decimal]]] = {
            region: defaultdict(lambda: defaultdict(lambda: Decimal("0")))
            for region in REPORT_REGION_GROUPS
        }

        for row in rows:
            normalized = self.normalizer.normalize_number_detail_item(row)

            region_group = normalized["region_group"]
            bet_type = normalized["bet_type"]
            region_key = normalized["region_key"]
            number_key = normalized["number_key"]
            amount = normalized["amount"]

            if region_group not in aggregated:
                continue

            if not bet_type or not region_key or not number_key:
                continue

            key = (region_key, number_key)
            aggregated[region_group][bet_type][key] += amount

        regions: dict[str, dict[str, Any]] = {}

        for region_group in REPORT_REGION_GROUPS:
            bet_types_data: dict[str, dict[str, list[dict[str, Any]]]] = {}
            has_data = False

            all_bet_types = list(REPORT_BET_TYPE_ORDER)
            extra_types = sorted(
                set(aggregated[region_group].keys()) - set(REPORT_BET_TYPE_ORDER)
            )
            all_bet_types.extend(extra_types)

            for bet_type in all_bet_types:
                raw_items = aggregated[region_group].get(bet_type, {})
                if not raw_items:
                    continue

                items = [
                    {
                        "region_key": region_key,
                        "number_key": number_key,
                        "bet_type": bet_type,
                        "amount": amount,
                    }
                    for (region_key, number_key), amount in raw_items.items()
                ]

                items.sort(
                    key=lambda x: (
                        -float(x["amount"]),
                        x["region_key"],
                        x["number_key"],
                    )
                )

                bet_types_data[bet_type] = {
                    "telegram_items": items[:50],
                    "html_items": items,
                }
                has_data = True

            regions[region_group] = {
                "has_data": has_data,
                "bet_types": bet_types_data,
            }

        return {
            "date": target_date,
            "regions": regions,
        }