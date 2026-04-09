from __future__ import annotations

from src.modules.result.repositories.draw_results_repository import DrawResultsRepository
from src.modules.settlement.repositories.settlement_repository import SettlementRepository
from src.modules.settlement.selectors.bet_selector import get_bets_for_settlement
from src.modules.settlement.settlement_engine import SettlementEngine


def settle_region(draw_date: str, region_group: str) -> dict:
    """
    指定日期 + 区域组执行结算。

    关键修正：
    1. 每次都允许重跑 settlement，避免旧的错误结算结果一直被锁住。
    2. 重跑前先清掉该日期 + 区域组的旧 settlement 结果。
    3. 只要开奖结果已经 available，就按当前最新 bet/result 重新计算。
    """

    normalized_draw_date = str(draw_date).strip()
    normalized_region_group = str(region_group).strip().upper()

    settlement_repo = SettlementRepository()
    draw_results_repo = DrawResultsRepository()

    draw_result = draw_results_repo.get_result(normalized_draw_date, normalized_region_group)
    if draw_result is None:
        return {
            "ok": False,
            "message": f"Draw result not found for {normalized_region_group} on {normalized_draw_date}",
            "draw_date": normalized_draw_date,
            "region_group": normalized_region_group,
            "draw_result_id": None,
            "total_bets": 0,
            "total_payout": 0,
            "results": [],
            "already_settled": False,
        }

    if str(draw_result.get("status", "")).strip().lower() != "available":
        return {
            "ok": False,
            "message": f"Draw result not available yet for {normalized_region_group} on {normalized_draw_date}",
            "draw_date": normalized_draw_date,
            "region_group": normalized_region_group,
            "draw_result_id": draw_result.get("id"),
            "total_bets": 0,
            "total_payout": 0,
            "results": [],
            "already_settled": False,
        }

    # 关键：不要被旧 run 锁死，直接清掉旧结果后按最新数据重算
    settlement_repo.clear_settlement_for_date_region(normalized_draw_date, normalized_region_group)

    bets = get_bets_for_settlement(normalized_draw_date, normalized_region_group)

    if not bets:
        settlement_repo.create_settlement_run(
            draw_date=normalized_draw_date,
            region_group=normalized_region_group,
            draw_result_id=draw_result["id"],
            total_bets=0,
            total_payout=0,
        )

        return {
            "ok": True,
            "message": f"No accepted bets found for {normalized_region_group} on {normalized_draw_date}",
            "draw_date": normalized_draw_date,
            "region_group": normalized_region_group,
            "draw_result_id": draw_result["id"],
            "total_bets": 0,
            "total_payout": 0,
            "results": [],
            "already_settled": False,
        }

    engine = SettlementEngine()
    settlement_results = engine.settle(bets, normalized_region_group)
    total_payout = sum(float(result.payout or 0) for result in settlement_results)

    settlement_repo.create_settlement_run(
        draw_date=normalized_draw_date,
        region_group=normalized_region_group,
        draw_result_id=draw_result["id"],
        total_bets=len(settlement_results),
        total_payout=total_payout,
    )

    return {
        "ok": True,
        "message": f"Settlement completed for {normalized_region_group} on {normalized_draw_date}",
        "draw_date": normalized_draw_date,
        "region_group": normalized_region_group,
        "draw_result_id": draw_result["id"],
        "total_bets": len(settlement_results),
        "total_payout": total_payout,
        "results": [result.to_dict() for result in settlement_results],
        "already_settled": False,
    }
