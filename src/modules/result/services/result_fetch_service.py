from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from src.modules.result.parsers.xosodaiphat_result_parser import XosodaiphatResultParser
from src.modules.result.providers.xosodaiphat_provider import XosodaiphatProvider
from src.modules.result.repositories.draw_result_items_repository import (
    DrawResultItemsRepository,
)
from src.modules.result.repositories.draw_results_repository import DrawResultsRepository


class ResultFetchService:
    EXPECTED_SUBREGION_RANGES = {
        "MN": (3, 4),
        "MT": (2, 3),
        "MB": (1, 1),
    }

    EXPECTED_PRIZE_SPECS = {
        "MN": XosodaiphatResultParser.MN_MT_PRIZE_SPEC,
        "MT": XosodaiphatResultParser.MN_MT_PRIZE_SPEC,
        "MB": XosodaiphatResultParser.MB_PRIZE_SPEC,
    }

    def __init__(self):
        self.results_repo = DrawResultsRepository()
        self.items_repo = DrawResultItemsRepository()

    def _load_items(self, draw_result_id: int) -> list[dict]:
        return self.items_repo.find_by_draw_result_id(draw_result_id)

    def _count_distinct_subregions_from_items(self, items: list[dict]) -> int:
        subregions = {
            str(item.get("sub_region_code", "")).strip().upper()
            for item in items
            if str(item.get("sub_region_code", "")).strip()
        }
        return len(subregions)

    def _is_items_complete(self, region_code: str, items: list[dict]) -> bool:
        region = str(region_code).upper().strip()
        if not items:
            return False

        min_subregions, max_subregions = self.EXPECTED_SUBREGION_RANGES.get(region, (1, 1))
        actual_subregions = self._count_distinct_subregions_from_items(items)
        if not (min_subregions <= actual_subregions <= max_subregions):
            return False

        expected_prize_specs = self.EXPECTED_PRIZE_SPECS.get(region, {})
        if not expected_prize_specs:
            return False

        prize_map: dict[str, dict[str, int]] = {}
        for item in items:
            sub_region_code = str(item.get("sub_region_code", "")).strip().upper()
            prize_code = str(item.get("prize_code", "")).strip().upper()
            if not sub_region_code or not prize_code:
                return False
            prize_map.setdefault(sub_region_code, {})
            prize_map[sub_region_code][prize_code] = prize_map[sub_region_code].get(prize_code, 0) + 1

        if not (min_subregions <= len(prize_map) <= max_subregions):
            return False

        for _, prize_counts in prize_map.items():
            for prize_code, spec in expected_prize_specs.items():
                if prize_counts.get(prize_code, 0) != int(spec["count"]):
                    return False

            for prize_code in prize_counts.keys():
                if prize_code not in expected_prize_specs:
                    return False

        return True

    def is_result_complete(self, draw_date: str, region_code: str) -> bool:
        region = region_code.upper().strip()
        row = self.results_repo.get_result(draw_date, region)

        if row is None:
            return False

        if str(row.get("status", "")).strip().lower() != "available":
            return False

        result_id = row["id"]
        items = self._load_items(result_id)
        return self._is_items_complete(region, items)

    def fetch_and_store(self, draw_date: str, region_code: str) -> Dict[str, Any]:
        """
        抓取网页 -> 解析 -> 入库

        返回:
        {
            "result_id": int,
            "status": "available" | "not_available"
        }
        """
        region = region_code.upper().strip()

        provider_result = XosodaiphatProvider.fetch_raw_html(region, draw_date)
        source_url = provider_result["source_url"]
        html = provider_result["html"]

        parsed_items = XosodaiphatResultParser.parse(region, draw_date, html)
        parsed_complete = self._is_items_complete(region, parsed_items)

        fetched_at = datetime.utcnow().isoformat(" ")
        source_name = "xosodaiphat"

        existing = self.results_repo.get_result(draw_date, region)
        status = "available" if parsed_complete else "not_available"

        if existing is None:
            result_id = self.results_repo.insert_result(
                draw_date=draw_date,
                region_code=region,
                source_name=source_name,
                source_url=source_url,
                status=status,
                fetched_at=fetched_at,
            )

            if parsed_complete:
                self.items_repo.insert_items(result_id, parsed_items)

            return {"result_id": result_id, "status": status}

        result_id = existing["id"]
        existing_items = self._load_items(result_id)

        self.results_repo.update_result_record(
            draw_result_id=result_id,
            status="available" if parsed_complete else "not_available",
            fetched_at=fetched_at,
            source_name=source_name,
            source_url=source_url,
        )

        if parsed_complete:
            if existing_items:
                self.items_repo.delete_by_draw_result_id(result_id)
            self.items_repo.insert_items(result_id, parsed_items)
            return {"result_id": result_id, "status": "available"}

        if existing_items:
            self.items_repo.delete_by_draw_result_id(result_id)

        return {"result_id": result_id, "status": "not_available"}
