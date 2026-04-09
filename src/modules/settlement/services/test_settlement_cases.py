from pprint import pprint

from src.modules.settlement.services.settlement_engine import SettlementEngine


def _run_case(case_name: str, bet: dict, region_group: str, expected_payout: int = None):
    print(f"\n===== {case_name} =====")

    engine = SettlementEngine()
    results = engine.settle([bet], region_group)

    if not results:
        raise ValueError(f"{case_name}: no settlement results returned")

    result = results[0]
    pprint(result.__dict__)

    if expected_payout is not None:
        assert result.payout == expected_payout, (
            f"{case_name}: expected payout={expected_payout}, got {result.payout}"
        )

    print(f"{case_name}: PASSED")


def main():
    # 1) 已验证通过的真实案例
    _run_case(
        case_name="LO 2C - BT - 69 x 5",
        bet={
            "id": 1,
            "bet_type": "LO",
            "bet_code": "2C",
            "bet_date": "2026-03-17",
            "regions": ["bt"],
            "number": "69",
            "unit": 5,
            "status": "accepted",
        },
        region_group="MN",
        expected_payout=350,
    )

    # 2) 未中案例（用于确认 hit=0 正常）
    _run_case(
        case_name="LO 2C - BT - 00 x 5",
        bet={
            "id": 2,
            "bet_type": "LO",
            "bet_code": "2C",
            "bet_date": "2026-03-17",
            "regions": ["bt"],
            "number": "00",
            "unit": 5,
            "status": "accepted",
        },
        region_group="MN",
        expected_payout=0,
    )

    # 下面这些先跑通结构，不先写死 expected_payout
    # 真实中不中由当前开奖数据决定

    _run_case(
        case_name="LO 3C - BT",
        bet={
            "id": 3,
            "bet_type": "LO",
            "bet_code": "3C",
            "bet_date": "2026-03-17",
            "regions": ["bt"],
            "number": "069",
            "unit": 1,
            "status": "accepted",
        },
        region_group="MN",
    )

    _run_case(
        case_name="LO 4C - BT",
        bet={
            "id": 4,
            "bet_type": "LO",
            "bet_code": "4C",
            "bet_date": "2026-03-17",
            "regions": ["bt"],
            "number": "4069",
            "unit": 1,
            "status": "accepted",
        },
        region_group="MN",
    )

    _run_case(
        case_name="DD 2C - BT",
        bet={
            "id": 5,
            "bet_type": "DD",
            "bet_code": "2C",
            "bet_date": "2026-03-17",
            "regions": ["bt"],
            "number": "69",
            "unit": 1,
            "status": "accepted",
        },
        region_group="MN",
    )

    _run_case(
        case_name="XC 3C - BT",
        bet={
            "id": 6,
            "bet_type": "XC",
            "bet_code": "3C",
            "bet_date": "2026-03-17",
            "regions": ["bt"],
            "number": "069",
            "unit": 1,
            "status": "accepted",
        },
        region_group="MN",
    )

    _run_case(
        case_name="XC 4C - BT",
        bet={
            "id": 7,
            "bet_type": "XC",
            "bet_code": "4C",
            "bet_date": "2026-03-17",
            "regions": ["bt"],
            "number": "4069",
            "unit": 1,
            "status": "accepted",
        },
        region_group="MN",
    )

    _run_case(
        case_name="DA 2C - BT",
        bet={
            "id": 8,
            "bet_type": "DA",
            "bet_code": "2C",
            "bet_date": "2026-03-17",
            "regions": ["bt"],
            "numbers": ["69", "77", "10"],
            "unit": 1,
            "status": "accepted",
        },
        region_group="MN",
    )

    _run_case(
        case_name="DX 2C - BT+VT",
        bet={
            "id": 9,
            "bet_type": "DX",
            "bet_code": "2C",
            "bet_date": "2026-03-17",
            "regions": ["bt", "vt"],
            "numbers": ["69", "77", "10"],
            "unit": 1,
            "status": "accepted",
        },
        region_group="MN",
    )

    print("\nALL TEST CASES COMPLETED.")


if __name__ == "__main__":
    main()