import os
import sqlite3
from pathlib import Path
from typing import Any

from src.app.database import get_db_path

class ReportRepository:
    def __init__(self, db_path: str | Path | None = None):
        self.db_path = Path(db_path) if db_path else None

    def _get_connection(self) -> sqlite3.Connection:
        db_path = self.db_path or get_db_path()
        db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def get_transaction_rows(self, target_date: str) -> list[dict[str, Any]]:
        """
        读取某天 accepted transaction rows。
        每一行对应 bet_items 的一条记录，并携带所属 batch 信息。
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT
                    bb.id AS batch_id,
                    bb.batch_code,
                    bb.user_id,
                    bb.region_group,
                    bb.bet_date,
                    bb.line_count,
                    bb.batch_total,
                    bb.created_at AS batch_created_at,
                    bb.updated_at AS batch_updated_at,

                    bi.id AS item_id,
                    bi.sequence_no,
                    bi.ticket_no,
                    bi.region_code,
                    bi.bet_type,
                    bi.number_mode,
                    bi.amount,
                    bi.input_text,
                    bi.total AS item_total,
                    bi.created_at AS item_created_at,
                    bi.updated_at AS item_updated_at
                FROM bet_batches bb
                INNER JOIN bet_items bi
                    ON bi.batch_id = bb.id
                WHERE bb.bet_date = ?
                  AND bb.status = 'accepted'
                  AND bi.status = 'accepted'
                ORDER BY
                    bb.region_group ASC,
                    bb.created_at ASC,
                    bb.id ASC,
                    bi.sequence_no ASC,
                    bi.id ASC
                """,
                (target_date,),
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def get_number_detail_rows(self, target_date: str) -> list[dict[str, Any]]:
        """
        读取某天 accepted number detail rows。
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT
                    bb.id AS batch_id,
                    bb.region_group,
                    bb.bet_date,
                    bb.created_at AS batch_created_at,

                    bi.id AS item_id,
                    bi.sequence_no,
                    bi.ticket_no,
                    bi.region_code,
                    bi.bet_type,
                    bi.number_mode,
                    bi.amount,
                    bi.input_text,
                    bi.total AS item_total,
                    bi.created_at AS item_created_at
                FROM bet_batches bb
                INNER JOIN bet_items bi
                    ON bi.batch_id = bb.id
                WHERE bb.bet_date = ?
                  AND bb.status = 'accepted'
                  AND bi.status = 'accepted'
                ORDER BY
                    bb.region_group ASC,
                    bi.bet_type ASC,
                    bb.created_at ASC,
                    bi.sequence_no ASC,
                    bi.id ASC
                """,
                (target_date,),
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()
