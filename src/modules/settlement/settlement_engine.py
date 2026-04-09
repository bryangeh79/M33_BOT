from __future__ import annotations

from typing import Dict, List

from src.modules.settlement.calculators.payout_calculator import calculate_payout
from src.modules.settlement.models.settlement_result import SettlementResult
from src.modules.settlement.repositories.settlement_repository import SettlementRepository
from src.modules.settlement.selectors.result_selector import get_results_by_region


def _normalize_bet_type(bet_type: str) -> str:
    text = str(bet_type or "").strip().upper()

    if text.startswith("LO"):
        return "LO"
    if text.startswith("DD"):
        return "DD"
    if text.startswith("XC"):
        return "XC"
    if text.startswith("DA"):
        return "DA"
    if text.startswith("DX"):
        return "DX"

    return text


def _normalize_region_code_for_lookup(value: str) -> str:
    return str(value or "").strip().upper()


def _normalize_region_code_for_storage(value: str) -> str:
    return str(value or "").strip().lower()


class SettlementEngine:
    def __init__(self):
        self.repository = SettlementRepository()

    def settle(self, bets: List[Dict], region_group: str) -> List[SettlementResult]:
        results: list[SettlementResult] = []

        normalized_region_group = str(region_group or "").strip().upper()

        for bet in bets:
            if str(bet.get("status", "")).strip().lower() != "accepted":
                continue

            bet_date = str(bet.get("bet_date", "")).strip()
            raw_regions = bet.get("regions") or []

            lookup_regions = [
                _normalize_region_code_for_lookup(region_code)
                for region_code in raw_regions
                if str(region_code or "").strip()
            ]

            storage_regions = [
                _normalize_region_code_for_storage(region_code)
                for region_code in raw_regions
                if str(region_code or "").strip()
            ]

            if not bet_date or not lookup_regions:
                continue

            normalized_bet = dict(bet)
            normalized_bet["bet_type"] = _normalize_bet_type(bet.get("bet_type", ""))
            normalized_bet["regions"] = storage_regions

            draw_results_by_region: dict[str, dict] = {}

            for region_code in lookup_regions:
                draw_results_by_region[region_code] = get_results_by_region(
                    draw_date=bet_date,
                    region_group=normalized_region_group,
                    sub_region_code=region_code,
                )

            payout, win_details = calculate_payout(
                bet=normalized_bet,
                draw_results_by_region=draw_results_by_region,
                region_group=normalized_region_group,
            )

            results.append(
                SettlementResult(
                    bet_id=normalized_bet.get("id"),
                    region=",".join(storage_regions),
                    bet_type=normalized_bet.get("bet_type", ""),
                    payout=payout,
                    win_details=win_details,
                )
            )

        if results:
            self.repository.save_many(results)

        return results
