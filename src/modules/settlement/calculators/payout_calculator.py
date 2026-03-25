from typing import Dict, Tuple


def calculate_payout(bet: dict, draw_results_by_region: Dict, region_group: str) -> Tuple[float, dict]:
    bet_type = str(bet.get("bet_type", "")).upper()
    numbers = bet.get("numbers", [])
    unit = int(bet.get("unit", 0))

    total_payout = 0
    wins = []
    total_wins = 0

    if bet_type.startswith("LO"):
        for region, result in draw_results_by_region.items():
            draw_numbers = result.get("numbers_2d", [])

            for n in numbers:
                n = str(n).zfill(2)
                hit_count = draw_numbers.count(n)

                if hit_count > 0:
                    payout = unit * 70 * hit_count
                    total_payout += payout
                    total_wins += hit_count

                    wins.append({
                        "region": region,
                        "number": n,
                        "hit_count": hit_count,
                        "payout": payout
                    })

    return total_payout, {
        "wins": wins,
        "total_wins": total_wins
    }
