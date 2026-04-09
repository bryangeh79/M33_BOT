from __future__ import annotations

from typing import Any, Dict, List

from src.modules.result.repositories.draw_result_items_repository import (
    DrawResultItemsRepository,
)
from src.modules.result.repositories.draw_results_repository import DrawResultsRepository
from src.modules.result.services.result_fetch_service import ResultFetchService


class ResultQueryService:
    def __init__(self):
        self.results_repo = DrawResultsRepository()
        self.items_repo = DrawResultItemsRepository()
        self.fetch_service = ResultFetchService()

    def get_or_fetch(self, draw_date: str, region_code: str) -> Dict[str, Any]:
        """
        行为规则：
        1. 如果没有记录 -> 抓取
        2. 如果已有 available 但结果不完整 -> 再抓一次
        3. 如果已有 not_available -> 自动再抓一次，再返回最新结果

        返回:
        {
            "meta": draw_results row dict | None,
            "items": [item_dict, ...]
        }
        """

        region = region_code.upper().strip()
        row = self.results_repo.get_result(draw_date, region)

        should_refetch = False
        if row is None:
            should_refetch = True
        else:
            status = str(row.get("status") or "").lower().strip()
            if status != "available":
                should_refetch = True
            elif not self.fetch_service.is_result_complete(draw_date, region):
                should_refetch = True

        if should_refetch:
            self.fetch_service.fetch_and_store(draw_date, region)
            row = self.results_repo.get_result(draw_date, region)

        if row is None:
            return {"meta": None, "items": []}

        result_id = row["id"]
        items: List[dict] = []

        if self.fetch_service.is_result_complete(draw_date, region):
            items = self.items_repo.find_by_draw_result_id(result_id)
            row["status"] = "available"
        else:
            row["status"] = "not_available"

        return {
            "meta": row,
            "items": items,
        }
