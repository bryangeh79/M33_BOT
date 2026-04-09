from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path
from typing import List

from src.modules.settlement.models.settlement_result import SettlementResult
from src.app.database import get_db_path


class SettlementRepository:
    def __init__(self, db_path: Path | None = None):
        self.db_path = db_path

    def _resolve_db_path(self) -> Path:
        if self.db_path is not None:
            return Path(self.db_path)
        return Path(get_db_path())

    def _get_connection(self):
        db_path = self._resolve_db_path()
        db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def save(self, settlement_result: SettlementResult) -> int:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO settlement_results (
                    bet_id,
                    region,
                    bet_type,
                    payout,
                    win_details
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    settlement_result.bet_id,
                    settlement_result.region,
                    settlement_result.bet_type,
                    settlement_result.payout,
                    json.dumps(settlement_result.win_details, ensure_ascii=False),
                ),
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def save_many(self, settlement_results: List[SettlementResult]) -> List[int]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            inserted_ids: list[int] = []

            for settlement_result in settlement_results:
                cursor.execute(
                    """
                    INSERT INTO settlement_results (
                        bet_id,
                        region,
                        bet_type,
                        payout,
                        win_details
                    )
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        settlement_result.bet_id,
                        settlement_result.region,
                        settlement_result.bet_type,
                        settlement_result.payout,
                        json.dumps(settlement_result.win_details, ensure_ascii=False),
                    ),
                )
                inserted_ids.append(cursor.lastrowid)

            conn.commit()
            return inserted_ids
        finally:
            conn.close()

    def find_by_bet_id(self, bet_id: int):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT *
                FROM settlement_results
                WHERE bet_id = ?
                ORDER BY id DESC
                """,
                (bet_id,),
            )

            rows = cursor.fetchall()

            results = []
            for row in rows:
                row_dict = dict(row)
                win_details = row_dict.get("win_details")

                if win_details:
                    try:
                        row_dict["win_details"] = json.loads(win_details)
                    except Exception:
                        pass

                results.append(row_dict)

            return results
        finally:
            conn.close()

    def get_settlement_run(self, draw_date: str, region_group: str):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT *
                FROM settlement_runs
                WHERE draw_date = ?
                  AND region_group = ?
                ORDER BY id DESC
                LIMIT 1
                """,
                (draw_date, region_group),
            )
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def clear_settlement_for_date_region(self, draw_date: str, region_group: str) -> None:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            cursor.execute(
                """
                DELETE FROM settlement_results
                WHERE bet_id IN (
                    SELECT bi.id
                    FROM bet_items bi
                    INNER JOIN bet_batches bb
                        ON bb.id = bi.batch_id
                    WHERE bb.bet_date = ?
                      AND bi.region_group = ?
                )
                """,
                (draw_date, region_group),
            )

            cursor.execute(
                """
                DELETE FROM settlement_runs
                WHERE draw_date = ?
                  AND region_group = ?
                """,
                (draw_date, region_group),
            )

            conn.commit()
        finally:
            conn.close()

    def create_settlement_run(
        self,
        draw_date: str,
        region_group: str,
        draw_result_id: int | None,
        total_bets: int,
        total_payout: float,
    ) -> int:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO settlement_runs (
                    draw_date,
                    region_group,
                    draw_result_id,
                    total_bets,
                    total_payout,
                    status
                )
                VALUES (?, ?, ?, ?, ?, 'completed')
                """,
                (
                    draw_date,
                    region_group,
                    draw_result_id,
                    total_bets,
                    total_payout,
                ),
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()
