from __future__ import annotations

from collections import Counter
from itertools import combinations
from typing import Dict, Tuple


def _normalize_digits(value: str, digits: int) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    return text[-digits:].zfill(digits)


def _normalize_region(region: str) -> str:
    return str(region or "").strip().upper()


def _safe_int(value) -> int:
    try:
        return int(float(str(value).strip()))
    except Exception:
        return 0


def _get_numbers_by_digits(result: dict, digits: int) -> list[str]:
    if digits == 2:
        values = result.get("numbers_2d", []) or []
    elif digits == 3:
        values = result.get("numbers_3d", []) or []
    elif digits == 4:
        values = result.get("numbers_4d", []) or []
    else:
        values = []

    return [_normalize_digits(v, digits) for v in values if str(v).strip()]


def _get_layer_values(result: dict, layer_key: str) -> list[str]:
    layers = result.get("layers", {}) or {}
    values = layers.get(layer_key, []) or []
    return [str(v).strip() for v in values if str(v).strip()]


def _region_has_number(result: dict, number: str, digits: int) -> bool:
    target = _normalize_digits(number, digits)
    if not target:
        return False
    values = _get_numbers_by_digits(result, digits)
    return target in values


def _region_hit_count(result: dict, number: str, digits: int) -> int:
    target = _normalize_digits(number, digits)
    if not target:
        return 0
    values = _get_numbers_by_digits(result, digits)
    return Counter(values).get(target, 0)


def _rate_for(region_group: str, bet_type: str, digits: int) -> int:
    group = str(region_group or "").strip().upper()
    kind = str(bet_type or "").strip().upper()

    if kind == "LO":
        if digits == 2:
            return 75 if group == "MB" else 70
        if digits == 3:
            return 600
        if digits == 4:
            return 6000

    if kind == "DD" and digits == 2:
        return 75 if group == "MB" else 70

    if kind == "XC" and digits in (3, 4):
        return 600

    if kind == "DA" and digits == 2:
        return 600 if group == "MB" else 700

    if kind == "DX" and digits == 2:
        return 0 if group == "MB" else 500

    return 0


def _build_lo_like_wins(
    *,
    bet_type: str,
    bet: dict,
    draw_results_by_region: Dict[str, dict],
    region_group: str,
    digits: int,
) -> Tuple[int, dict]:
    unit = _safe_int(bet.get("unit", 0))
    rate = _rate_for(region_group, bet_type, digits)

    total_payout = 0
    wins = []
    total_wins = 0

    if unit <= 0 or rate <= 0:
        return 0, {"wins": [], "total_wins": 0}

    numbers = [_normalize_digits(n, digits) for n in (bet.get("numbers") or []) if str(n).strip()]
    if not numbers:
        single_number = str(bet.get("number", "")).strip()
        if single_number:
            numbers = [_normalize_digits(single_number, digits)]

    for region, result in draw_results_by_region.items():
        for n in numbers:
            hit_count = _region_hit_count(result, n, digits)
            if hit_count <= 0:
                continue

            payout = unit * rate * hit_count
            total_payout += payout
            total_wins += hit_count
            wins.append(
                {
                    "region": _normalize_region(region),
                    "number": n,
                    "hit_count": hit_count,
                    "payout": payout,
                    "bet_type": bet_type,
                    "digits": digits,
                }
            )

    return total_payout, {"wins": wins, "total_wins": total_wins}


def _dd_exact_layer_key(region_group: str) -> str:
    group = str(region_group or "").strip().upper()
    if group == "MB":
        return "g7"
    return "g8"


def _build_dd_wins(
    *,
    bet: dict,
    draw_results_by_region: Dict[str, dict],
    region_group: str,
) -> Tuple[int, dict]:
    unit = _safe_int(bet.get("unit", 0))
    rate = _rate_for(region_group, "DD", 2)

    if unit <= 0 or rate <= 0:
        return 0, {"wins": [], "total_wins": 0}

    numbers = [_normalize_digits(n, 2) for n in (bet.get("numbers") or []) if str(n).strip()]
    if not numbers:
        single_number = str(bet.get("number", "")).strip()
        if single_number:
            numbers = [_normalize_digits(single_number, 2)]

    exact_layer_key = _dd_exact_layer_key(region_group)

    total_payout = 0
    wins = []
    total_wins = 0

    for region, result in draw_results_by_region.items():
        exact_values = [_normalize_digits(v, 2) for v in _get_layer_values(result, exact_layer_key)]
        db_values = [_normalize_digits(v, 2) for v in _get_layer_values(result, "db")]

        for n in numbers:
            hit_sources = []

            if n in exact_values:
                hit_sources.append(exact_layer_key.upper())

            if n in db_values:
                hit_sources.append("DB")

            hit_count = len(hit_sources)
            if hit_count <= 0:
                continue

            payout = unit * rate * hit_count
            total_payout += payout
            total_wins += hit_count
            wins.append(
                {
                    "region": _normalize_region(region),
                    "number": n,
                    "hit_count": hit_count,
                    "hit_sources": hit_sources,
                    "payout": payout,
                    "bet_type": "DD",
                    "digits": 2,
                }
            )

    return total_payout, {"wins": wins, "total_wins": total_wins}


def _build_da_wins(
    *,
    bet: dict,
    draw_results_by_region: Dict[str, dict],
    region_group: str,
) -> Tuple[int, dict]:
    unit = _safe_int(bet.get("unit", 0))
    rate = _rate_for(region_group, "DA", 2)

    if unit <= 0 or rate <= 0:
        return 0, {"wins": [], "total_wins": 0}

    raw_numbers = [_normalize_digits(n, 2) for n in (bet.get("numbers") or []) if str(n).strip()]
    pair_numbers = list(combinations(raw_numbers, 2))

    total_payout = 0
    wins = []
    total_wins = 0

    for region, result in draw_results_by_region.items():
        for first, second in pair_numbers:
            first_count = _region_hit_count(result, first, 2)
            second_count = _region_hit_count(result, second, 2)
            hit_count = min(first_count, second_count)

            if hit_count <= 0:
                continue

            payout = unit * rate * hit_count
            total_payout += payout
            total_wins += hit_count
            wins.append(
                {
                    "region": _normalize_region(region),
                    "number_group": f"{first} {second}",
                    "hit_count": hit_count,
                    "payout": payout,
                    "bet_type": "DA",
                }
            )

    return total_payout, {"wins": wins, "total_wins": total_wins}


def _build_dx_wins(
    *,
    bet: dict,
    draw_results_by_region: Dict[str, dict],
    region_group: str,
) -> Tuple[int, dict]:
    unit = _safe_int(bet.get("unit", 0))
    rate = _rate_for(region_group, "DX", 2)

    if unit <= 0 or rate <= 0:
        return 0, {"wins": [], "total_wins": 0}

    raw_numbers = [_normalize_digits(n, 2) for n in (bet.get("numbers") or []) if str(n).strip()]
    unique_numbers = []
    for n in raw_numbers:
        if n not in unique_numbers:
            unique_numbers.append(n)

    if len(unique_numbers) < 2:
        return 0, {"wins": [], "total_wins": 0}

    region_codes = list(draw_results_by_region.keys())
    if len(region_codes) < 2:
        return 0, {"wins": [], "total_wins": 0}

    number_pairs = list(combinations(unique_numbers, 2))
    region_pairs = list(combinations(region_codes, 2))

    total_payout = 0
    wins = []
    total_wins = 0

    for first, second in number_pairs:
        for region_a, region_b in region_pairs:
            result_a = draw_results_by_region.get(region_a, {}) or {}
            result_b = draw_results_by_region.get(region_b, {}) or {}

            count_a_first = _region_hit_count(result_a, first, 2)
            count_a_second = _region_hit_count(result_a, second, 2)
            count_b_first = _region_hit_count(result_b, first, 2)
            count_b_second = _region_hit_count(result_b, second, 2)

            direct_count = min(count_a_first, count_b_second)
            reverse_count = min(count_a_second, count_b_first)
            single_a_count = min(count_a_first, count_a_second)
            single_b_count = min(count_b_first, count_b_second)

            pair_hit_count = 0
            hit_sources = []

            if direct_count > 0:
                pair_hit_count += direct_count
                hit_sources.append(f"direct:{direct_count}")

            if reverse_count > 0:
                pair_hit_count += reverse_count
                hit_sources.append(f"reverse:{reverse_count}")

            if single_a_count > 0:
                pair_hit_count += single_a_count
                hit_sources.append(f"single:{_normalize_region(region_a)}:{single_a_count}")

            if single_b_count > 0:
                pair_hit_count += single_b_count
                hit_sources.append(f"single:{_normalize_region(region_b)}:{single_b_count}")

            if pair_hit_count <= 0:
                continue

            payout = unit * rate * pair_hit_count
            total_payout += payout
            total_wins += pair_hit_count
            wins.append(
                {
                    "region_pair": f"{_normalize_region(region_a)},{_normalize_region(region_b)}",
                    "number_group": f"{first} {second}",
                    "hit_count": pair_hit_count,
                    "hit_sources": hit_sources,
                    "payout": payout,
                    "bet_type": "DX",
                }
            )

    return total_payout, {"wins": wins, "total_wins": total_wins}


def calculate_payout(bet: dict, draw_results_by_region: Dict, region_group: str) -> Tuple[float, dict]:
    bet_type = str(bet.get("bet_type", "")).upper().strip()

    if bet_type == "LO":
        numbers = bet.get("numbers", []) or []
        digits = len(str(numbers[0]).strip()) if numbers else len(str(bet.get("number", "")).strip())
        return _build_lo_like_wins(
            bet_type="LO",
            bet=bet,
            draw_results_by_region=draw_results_by_region,
            region_group=region_group,
            digits=digits,
        )

    if bet_type == "DD":
        return _build_dd_wins(
            bet=bet,
            draw_results_by_region=draw_results_by_region,
            region_group=region_group,
        )

    if bet_type == "XC":
        numbers = bet.get("numbers", []) or []
        digits = len(str(numbers[0]).strip()) if numbers else len(str(bet.get("number", "")).strip())
        return _build_lo_like_wins(
            bet_type="XC",
            bet=bet,
            draw_results_by_region=draw_results_by_region,
            region_group=region_group,
            digits=digits,
        )

    if bet_type == "DA":
        return _build_da_wins(
            bet=bet,
            draw_results_by_region=draw_results_by_region,
            region_group=region_group,
        )

    if bet_type == "DX":
        return _build_dx_wins(
            bet=bet,
            draw_results_by_region=draw_results_by_region,
            region_group=region_group,
        )

    return 0, {"wins": [], "total_wins": 0}
