from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Any

from src.modules.report.repositories.settlement_report_repository import SettlementReportRepository
from src.modules.settlement.settlement_service import settle_region


class SettlementReportService:
    REGION_GROUPS = ("MN", "MT", "MB")

    def __init__(self, repository: SettlementReportRepository | None = None):
        self.repository = repository or SettlementReportRepository()

    @staticmethod
    def _to_float(value: Decimal) -> float:
        return float(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

    @staticmethod
    def _safe_rate(rate) -> Decimal:
        if rate is None:
            return Decimal("0")

        text = str(rate).strip()
        if not text or text.lower() == "none":
            return Decimal("0")

        try:
            return Decimal(text)
        except Exception:
            return Decimal("0")

    def _refresh_settlement(self, target_date: str) -> list[dict[str, str]]:
        errors: list[dict[str, str]] = []

        for region in self.REGION_GROUPS:
            try:
                result = settle_region(target_date, region)
                if not result.get("ok", False):
                    errors.append(
                        {
                            "region_group": region,
                            "message": str(result.get("message", "")).strip() or "Unknown error",
                        }
                    )
                for item in result.get("settlement_errors", []) or []:
                    ticket_no = str(item.get("ticket_no", "")).strip().upper() or "-"
                    input_text = str(item.get("input_text", "")).strip()
                    detail = str(item.get("message", "")).strip() or "Unknown error"
                    if input_text:
                        detail = f"{ticket_no} | {input_text} | {detail}"
                    else:
                        detail = f"{ticket_no} | {detail}"
                    errors.append(
                        {
                            "region_group": region,
                            "message": detail,
                        }
                    )
            except Exception as exc:
                errors.append(
                    {
                        "region_group": region,
                        "message": str(exc),
                    }
                )

        return errors

    def generate_report(
        self,
        target_date: str,
        agent_commission_rate: float | str | Decimal = 0,
    ) -> dict[str, Any]:
        settlement_errors = self._refresh_settlement(target_date)

        region_bet_totals = self.repository.get_region_bet_totals(target_date)
        region_payout_totals = self.repository.get_region_payout_totals(target_date)
        region_winner_counts = self.repository.get_region_winner_counts(target_date)
        winner_details = self.repository.get_winner_details(target_date)

        raw_rate = self._safe_rate(agent_commission_rate)
        commission_rate = (raw_rate / Decimal("100")).quantize(
            Decimal("0.0001"), rounding=ROUND_HALF_UP
        )

        regions: dict[str, dict[str, Any]] = {}

        total_settlement = Decimal("0")
        total_bet = Decimal("0")
        total_payout = Decimal("0")
        total_commission = Decimal("0")

        for region in self.REGION_GROUPS:
            bet_total = region_bet_totals.get(region, Decimal("0"))
            payout_total = region_payout_totals.get(region, Decimal("0"))
            winner_count = region_winner_counts.get(region, 0)

            commission = (bet_total * commission_rate).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )

            settlement = (bet_total - payout_total - commission).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )

            regions[region] = {
                "bet_total": self._to_float(bet_total),
                "payout_total": self._to_float(payout_total),
                "commission_rate_percent": self._to_float(raw_rate),
                "commission": self._to_float(commission),
                "settlement": self._to_float(settlement),
                "winner_count": winner_count,
            }

            total_bet += bet_total
            total_payout += payout_total
            total_commission += commission
            total_settlement += settlement

        normalized_winner_details = []
        for item in winner_details:
            normalized_winner_details.append(
                {
                    "ticket_no": item["ticket_no"],
                    "region_group": item["region_group"],
                    "region": item["region"],
                    "region_code": item["region_code"],
                    "bet_type": item["bet_type"],
                    "bet_code": item["bet_code"],
                    "numbers": item["numbers"],
                    "regions": item["regions"],
                    "bet_amount": self._to_float(item["bet_amount"]),
                    "bet_total": self._to_float(item["bet_total"]),
                    "payout": self._to_float(item["payout"]),
                    "input_text": item["input_text"],
                    "win_details": item["win_details"],
                    "display_region": item.get("display_region", item["region"]),
                    "display_number": item.get("display_number", " ".join(item["numbers"])),
                    "display_bet": self._to_float(item.get("display_bet", item["bet_total"])),
                }
            )

        return {
            "date": target_date,
            "regions": regions,
            "summary": {
                "agent_commission_rate_percent": self._to_float(raw_rate),
                "total_bet": self._to_float(total_bet),
                "total_payout": self._to_float(total_payout),
                "total_commission": self._to_float(total_commission),
                "total_settlement": self._to_float(total_settlement),
            },
            "winner_details": normalized_winner_details,
            "settlement_errors": settlement_errors,
        }
