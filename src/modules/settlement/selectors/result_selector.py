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


def get_results_by_region(draw_date: str, region_group: str, sub_region_code: str) -> Dict:
    draw_results_repo = DrawResultsRepository()
    draw_result_items_repo = DrawResultItemsRepository()

    result_row = draw_results_repo.get_result(draw_date, region_group)
    if result_row is None:
        raise ValueError(
            f"Draw result not found for draw_date={draw_date}, region_group={region_group}"
        )

    draw_result_id = result_row["id"]
    all_items = draw_result_items_repo.find_by_draw_result_id(draw_result_id)

    target_region = _normalize_target_sub_region_code(sub_region_code, region_group)

    region_items = [
        item for item in all_items
        if str(item.get("sub_region_code", "")).strip().upper() == target_region
    ]

    if not region_items:
        raise ValueError(
            f"Draw result items not found for draw_date={draw_date}, "
            f"region_group={region_group}, sub_region_code={sub_region_code}, "
            f"normalized={target_region}"
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
        "region_group": str(region_group).strip().upper(),
        "sub_region_code": target_region,
        "layers": layers,
        "numbers_2d": numbers_2d,
        "numbers_3d": numbers_3d,
        "numbers_4d": numbers_4d,
    }
