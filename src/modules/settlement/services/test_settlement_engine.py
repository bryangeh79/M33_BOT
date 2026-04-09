from pprint import pprint

from src.modules.settlement.services.settlement_engine import SettlementEngine


def main():
    bet = {
        "id": 1,
        "bet_type": "LO",
        "bet_code": "2C",
        "bet_date": "2026-03-17",
        "regions": ["bt"],
        "number": "69",
        "unit": 5,
        "status": "accepted",
    }

    engine = SettlementEngine()
    results = engine.settle([bet], "MN")

    if not results:
        raise ValueError("No settlement results returned")

    result = results[0]

    print("=== SETTLEMENT RESULT ===")
    pprint(result.__dict__)

    assert result.payout == 350, f"Expected payout=350, got {result.payout}"

    print("Settlement test passed.")


if __name__ == "__main__":
    main()