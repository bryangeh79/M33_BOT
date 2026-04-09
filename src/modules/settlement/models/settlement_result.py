class SettlementResult:

    def __init__(
        self,
        bet_id: int,
        region: str,
        bet_type: str,
        payout: float,
        win_details: dict
    ):
        self.bet_id = bet_id
        self.region = region
        self.bet_type = bet_type
        self.payout = payout
        self.win_details = win_details

    def to_dict(self):
        return {
            "bet_id": self.bet_id,
            "region": self.region,
            "bet_type": self.bet_type,
            "payout": self.payout,
            "win_details": self.win_details
        }