from __future__ import annotations

from src.modules.result.repositories.draw_results_repository import DrawResultsRepository
from src.modules.settlement.repositories.settlement_repository import SettlementRepository
from src.modules.settlement.selectors.bet_selector import get_bets_for_settlement
from src.modules.settlement.settlement_engine import SettlementEngine


def settle_region(draw_date: str, region_group: str) -> dict:
    region_group = str(region_group).strip().upper()

    settlement_repo = SettlementRepository()
    draw_results_repo = DrawResultsRepository()

    draw_result = draw_results_repo.get_result(draw_date, region_group)
    if draw_result is None:
        return {
            "ok": False,
            "message": f"Draw result not found for {region_group} on {draw_date}",
            "draw_date": draw_date,
            "region_group": region_group,
            "draw_result_id": None,
            "total_bets": 0,
            "total_payout": 0,
            "results": [],
            "already_settled": False,
        }

    if str(draw_result.get("status", "")).lower() != "available":
        return {
            "ok": False,
            "message": f"Draw result not available yet for {region_group} on {draw_date}",
            "draw_date": draw_date,
            "region_group": region_group,
            "draw_result_id": draw_result["id"],
            "total_bets": 0,
            "total_payout": 0,
            "results": [],
            "already_settled": False,
        }

    settlement_repo.clear_settlement_for_date_region(draw_date, region_group)

    bets = get_bets_for_settlement(draw_date, region_group)

    if not bets:
        settlement_repo.create_settlement_run(
            draw_date=draw_date,
            region_group=region_group,
            draw_result_id=draw_result["id"],
            total_bets=0,
            total_payout=0,
        )

        return {
            "ok": True,
            "message": f"No accepted bets found for {region_group} on {draw_date}",
            "draw_date": draw_date,
            "region_group": region_group,
            "draw_result_id": draw_result["id"],
            "total_bets": 0,
            "total_payout": 0,
            "results": [],
            "already_settled": False,
        }

    engine = SettlementEngine()
    settlement_results = engine.settle(bets, region_group)
    total_payout = sum(float(result.payout or 0) for result in settlement_results)

    settlement_repo.create_settlement_run(
        draw_date=draw_date,
        region_group=region_group,
        draw_result_id=draw_result["id"],
        total_bets=len(settlement_results),
        total_payout=total_payout,
    )

    return {
        "ok": True,
        "message": f"Settlement completed for {region_group} on {draw_date}",
        "draw_date": draw_date,
        "region_group": region_group,
        "draw_result_id": draw_result["id"],
        "total_bets": len(settlement_results),
        "total_payout": total_payout,
        "results": [result.to_dict() for result in settlement_results],
        "already_settled": False,
    }
