import json
import sqlite3
from decimal import Decimal

from src.app.database import get_db_path


class SettlementReportRepository:
    REGION_GROUPS = ("MN", "MT", "MB")

    def _get_connection(self):
        conn = sqlite3.connect(str(get_db_path()))
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def _to_decimal(value) -> Decimal:
        if value is None:
            return Decimal("0")

        text = str(value).strip()
        if not text or text.lower() == "none":
            return Decimal("0")

        try:
            return Decimal(text)
        except Exception:
            return Decimal("0")

    @staticmethod
    def _safe_json_loads(value, default):
        if value is None:
            return default

        text = str(value).strip()
        if not text or text.lower() == "none":
            return default

        try:
            return json.loads(text)
        except Exception:
            return default

    def get_region_bet_totals(self, target_date: str) -> dict[str, Decimal]:
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                bi.region_group,
                COALESCE(SUM(CAST(bi.total AS REAL)), 0) AS bet_total
            FROM settlement_results sr
            INNER JOIN bet_items bi
                ON bi.id = sr.bet_id
            INNER JOIN bet_batches bb
                ON bb.id = bi.batch_id
            WHERE bb.bet_date = ?
              AND bb.status = 'accepted'
              AND bi.status = 'accepted'
            GROUP BY bi.region_group
            """,
            (target_date,),
        )

        rows = cursor.fetchall()
        conn.close()

        result = {region: Decimal("0") for region in self.REGION_GROUPS}
        for row in rows:
            region_group = str(row["region_group"]).upper()
            if region_group in result:
                result[region_group] = self._to_decimal(row["bet_total"])

        return result

    def get_region_payout_totals(self, target_date: str) -> dict[str, Decimal]:
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                bi.region_group,
                COALESCE(SUM(CAST(sr.payout AS REAL)), 0) AS payout_total
            FROM settlement_results sr
            INNER JOIN bet_items bi
                ON bi.id = sr.bet_id
            INNER JOIN bet_batches bb
                ON bb.id = bi.batch_id
            WHERE bb.bet_date = ?
              AND bb.status = 'accepted'
              AND bi.status = 'accepted'
            GROUP BY bi.region_group
            """,
            (target_date,),
        )

        rows = cursor.fetchall()
        conn.close()

        result = {region: Decimal("0") for region in self.REGION_GROUPS}
        for row in rows:
            region_group = str(row["region_group"]).upper()
            if region_group in result:
                result[region_group] = self._to_decimal(row["payout_total"])

        return result

    def get_region_winner_counts(self, target_date: str) -> dict[str, int]:
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                bi.region_group,
                COUNT(*) AS winner_count
            FROM settlement_results sr
            INNER JOIN bet_items bi
                ON bi.id = sr.bet_id
            INNER JOIN bet_batches bb
                ON bb.id = bi.batch_id
            WHERE bb.bet_date = ?
              AND bb.status = 'accepted'
              AND bi.status = 'accepted'
              AND CAST(sr.payout AS REAL) > 0
            GROUP BY bi.region_group
            """,
            (target_date,),
        )

        rows = cursor.fetchall()
        conn.close()

        result = {region: 0 for region in self.REGION_GROUPS}
        for row in rows:
            region_group = str(row["region_group"]).upper()
            if region_group in result:
                result[region_group] = int(row["winner_count"] or 0)

        return result

    def _build_expanded_winner_rows(self, row_dict: dict) -> list[dict]:
        win_details = self._safe_json_loads(row_dict.get("win_details"), {}) or {}
        numbers = self._safe_json_loads(row_dict.get("numbers_json"), [])
        regions = self._safe_json_loads(row_dict.get("regions_json"), [])
        wins = win_details.get("wins", []) or []

        base_bet_amount = self._to_decimal(row_dict.get("amount"))
        base_bet_total = self._to_decimal(row_dict.get("total"))
        base_payout = self._to_decimal(row_dict.get("payout"))

        base_detail = {
            "settlement_result_id": row_dict["settlement_result_id"],
            "bet_id": row_dict["bet_id"],
            "ticket_no": str(row_dict.get("ticket_no", "")).strip().upper(),
            "region_group": str(row_dict.get("region_group", "")).strip().upper(),
            "region": str(row_dict.get("region", "")).strip(),
            "region_code": str(row_dict.get("region_code", "")).strip(),
            "bet_type": str(row_dict.get("bet_type", "")).strip().upper(),
            "bet_code": str(row_dict.get("bet_code", "")).strip().upper(),
            "numbers": [str(x).strip() for x in numbers if str(x).strip()],
            "regions": [str(x).strip().lower() for x in regions if str(x).strip()],
            "bet_amount": base_bet_amount,
            "bet_total": base_bet_total,
            "payout": base_payout,
            "input_text": str(row_dict.get("input_text", "")).strip(),
            "win_details": win_details,
            "display_region": str(row_dict.get("region", "")).strip().upper() or "-",
            "display_number": " ".join(str(x).strip() for x in numbers if str(x).strip()) or "-",
            "display_bet": base_bet_total,
        }

        if not wins:
            return [base_detail]

        expanded: list[dict] = []

        for index, win in enumerate(wins, start=1):
            win_region = (
                str(win.get("region_pair", "")).strip().upper()
                or str(win.get("region", "")).strip().upper()
                or base_detail["display_region"]
            )

            win_number = (
                str(win.get("number_group", "")).strip()
                or str(win.get("number", "")).strip()
                or base_detail["display_number"]
            )

            hit_count_raw = win.get("hit_count", 1)
            try:
                hit_count = int(hit_count_raw)
            except Exception:
                hit_count = 1
            if hit_count <= 0:
                hit_count = 1

            win_payout = self._to_decimal(win.get("payout"))
            row_bet = (base_bet_amount * Decimal(hit_count)) if base_bet_amount > 0 else base_bet_total

            expanded.append(
                {
                    **base_detail,
                    "settlement_result_id": f"{row_dict['settlement_result_id']}-{index}",
                    "region": win_region,
                    "payout": win_payout,
                    "display_region": win_region,
                    "display_number": win_number,
                    "display_bet": row_bet,
                    "win_entry": win,
                }
            )

        return expanded

    def get_winner_details(self, target_date: str) -> list[dict]:
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                sr.id AS settlement_result_id,
                sr.bet_id,
                sr.region,
                sr.bet_type,
                sr.payout,
                sr.win_details,

                bi.ticket_no,
                bi.region_group,
                bi.region_code,
                bi.bet_code,
                bi.amount,
                bi.total,
                bi.numbers_json,
                bi.regions_json,
                bi.input_text,

                bb.bet_date
            FROM settlement_results sr
            INNER JOIN bet_items bi
                ON bi.id = sr.bet_id
            INNER JOIN bet_batches bb
                ON bb.id = bi.batch_id
            WHERE bb.bet_date = ?
              AND bb.status = 'accepted'
              AND bi.status = 'accepted'
              AND CAST(sr.payout AS REAL) > 0
            ORDER BY sr.id ASC
            """,
            (target_date,),
        )

        rows = cursor.fetchall()
        conn.close()

        details: list[dict] = []

        for row in rows:
            row_dict = dict(row)
            details.extend(self._build_expanded_winner_rows(row_dict))

        details.sort(
            key=lambda item: (
                item.get("ticket_no", ""),
                str(item.get("display_region", "")),
                str(item.get("display_number", "")),
            )
        )
        return details
