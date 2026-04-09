from collections import OrderedDict
from decimal import Decimal
from typing import Any

from src.modules.report.constants.report_constants import REPORT_REGION_GROUPS
from src.modules.report.helpers.report_normalizer import ReportNormalizer
from src.modules.report.repositories.report_repository import ReportRepository


class TransactionReportService:
    def __init__(self, repository: ReportRepository | None = None):
        self.repository = repository or ReportRepository()

    def generate_report(self, target_date: str) -> dict[str, Any]:
        rows = self.repository.get_transaction_rows(target_date)

        regions: dict[str, dict[str, Any]] = {
            region: {
                "total_amount": Decimal("0"),
                "tickets": [],
                "has_data": False,
            }
            for region in REPORT_REGION_GROUPS
        }

        grouped: dict[str, OrderedDict[int, dict[str, Any]]] = {
            region: OrderedDict() for region in REPORT_REGION_GROUPS
        }

        for row in rows:
            region_group = str(row.get("region_group", "")).upper()
            if region_group not in grouped:
                continue

            batch_id = int(row["batch_id"])
            ticket_no = str(row.get("ticket_no", "")).upper()

            if batch_id not in grouped[region_group]:
                grouped[region_group][batch_id] = {
                    "batch_id": batch_id,
                    "ticket_no": ticket_no,
                    "lines": [],
                    "total_amount": ReportNormalizer.to_decimal(row.get("batch_total")),
                    "created_at": row.get("batch_created_at", ""),
                }

            grouped[region_group][batch_id]["lines"].append(
                ReportNormalizer.normalize_transaction_item(row)
            )

        grand_total = Decimal("0")

        for region_group in REPORT_REGION_GROUPS:
            tickets = list(grouped[region_group].values())
            total_amount = sum(
                (ticket["total_amount"] for ticket in tickets),
                start=Decimal("0"),
            )

            regions[region_group]["tickets"] = tickets
            regions[region_group]["total_amount"] = total_amount
            regions[region_group]["has_data"] = len(tickets) > 0

            grand_total += total_amount

        return {
            "date": target_date,
            "regions": regions,
            "grand_total": grand_total,
        }