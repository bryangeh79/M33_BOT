from typing import Dict, List

from src.modules.result.repositories.draw_results_repository import DrawResultsRepository
from src.modules.result.repositories.draw_result_items_repository import DrawResultItemsRepository
from src.modules.settlement.constants.region_aliases import normalize_region_alias


def _normalize_prize_code(prize_code: str) -> str:
    value = str(prize_code).strip().lower()
    value = value.replace(".", "_")
    return value


def _sort_layer_items(items: List[dict]) -> List[str]:
    sorted_items = sorted(items, key=lambda x: (x.get("item_order", 0)))
    return [str(item.get("number_value", "")).strip() for item in sorted_items if str(item.get("number_value", "")).strip()]


def _normalize_target_sub_region_code(sub_region_code: str, region_group: str) -> str:
    return normalize_region_alias(sub_region_code, region_group)


def _build_region_candidates(sub_region_code: str, region_group: str) -> set[str]:
    raw = str(sub_region_code or "").strip().upper()
    normalized = _normalize_target_sub_region_code(raw, region_group)

    candidates = {raw, normalized}

    if "," in raw:
        candidates.update(part.strip().upper() for part in raw.split(",") if part.strip())

    if "," in normalized:
        candidates.update(part.strip().upper() for part in normalized.split(",") if part.strip())

    return {value for value in candidates if value}


def _match_region_item(item_sub_region_code: str, target_candidates: set[str], region_group: str) -> bool:
    raw_item = str(item_sub_region_code or "").strip().upper()
    normalized_item = normalize_region_alias(raw_item, region_group)
    return raw_item in target_candidates or normalized_item in target_candidates


def get_results_by_region(draw_date: str, region_group: str, sub_region_code: str) -> Dict:
    draw_results_repo = DrawResultsRepository()
    draw_result_items_repo = DrawResultItemsRepository()

    region_group = str(region_group).strip().upper()

    result_row = draw_results_repo.get_result(draw_date, region_group)
    if result_row is None:
        raise ValueError(
            f"Draw result not found for draw_date={draw_date}, region_group={region_group}"
        )

    draw_result_id = result_row["id"]
    all_items = draw_result_items_repo.find_by_draw_result_id(draw_result_id)

    target_candidates = _build_region_candidates(sub_region_code, region_group)
    normalized_target = _normalize_target_sub_region_code(sub_region_code, region_group)

    region_items = [
        item for item in all_items
        if _match_region_item(item.get("sub_region_code", ""), target_candidates, region_group)
    ]

    if not region_items:
        available_regions = sorted(
            {
                str(item.get("sub_region_code", "")).strip().upper()
                for item in all_items
                if str(item.get("sub_region_code", "")).strip()
            }
        )
        raise ValueError(
            f"Draw result items not found for draw_date={draw_date}, "
            f"region_group={region_group}, sub_region_code={sub_region_code}, "
            f"normalized={normalized_target}, available={available_regions}"
        )

    grouped: Dict[str, List[dict]] = {}
    for item in region_items:
        layer_key = _normalize_prize_code(item.get("prize_code", ""))
        grouped.setdefault(layer_key, []).append(item)

    layers: Dict[str, List[str]] = {}
    all_numbers: List[str] = []

    for layer_key, items in grouped.items():
        values = _sort_layer_items(items)
        layers[layer_key] = values
        all_numbers.extend(values)

    numbers_2d = [num[-2:].zfill(2) for num in all_numbers if len(num) >= 2]
    numbers_3d = [num[-3:].zfill(3) for num in all_numbers if len(num) >= 3]
    numbers_4d = [num[-4:].zfill(4) for num in all_numbers if len(num) >= 4]

    return {
        "region_group": region_group,
        "sub_region_code": normalized_target,
        "layers": layers,
        "numbers_2d": numbers_2d,
        "numbers_3d": numbers_3d,
        "numbers_4d": numbers_4d,
    }
