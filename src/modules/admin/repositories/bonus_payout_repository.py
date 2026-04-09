import os
import sqlite3
from pathlib import Path

from src.app.database import get_db_path

class BonusPayoutRepository:
    def __init__(self, db_path: str | Path | None = None):
        self.db_path = Path(db_path) if db_path else None

    def _get_connection(self) -> sqlite3.Connection:
        db_path = self.db_path or get_db_path()
        db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def init_table(self) -> None:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS bonus_payout_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    payout_key TEXT NOT NULL UNIQUE,
                    payout_value TEXT NOT NULL,
                    is_active INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.commit()
        finally:
            conn.close()

    def ensure_defaults(self, defaults: dict[str, str]) -> None:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            for payout_key, payout_value in defaults.items():
                cursor.execute(
                    """
                    INSERT INTO bonus_payout_settings (payout_key, payout_value, is_active)
                    VALUES (?, ?, 1)
                    ON CONFLICT(payout_key) DO NOTHING
                    """,
                    (payout_key, str(payout_value)),
                )
            conn.commit()
        finally:
            conn.close()

    def get_all(self) -> dict[str, str]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT payout_key, payout_value
                FROM bonus_payout_settings
                WHERE is_active = 1
                ORDER BY payout_key ASC
                """
            )
            rows = cursor.fetchall()
            return {str(row['payout_key']): str(row['payout_value']) for row in rows}
        finally:
            conn.close()

    def upsert_many(self, values: dict[str, str]) -> None:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            for payout_key, payout_value in values.items():
                cursor.execute(
                    """
                    INSERT INTO bonus_payout_settings (payout_key, payout_value, is_active)
                    VALUES (?, ?, 1)
                    ON CONFLICT(payout_key) DO UPDATE SET
                        payout_value = excluded.payout_value,
                        is_active = 1,
                        updated_at = CURRENT_TIMESTAMP
                    """,
                    (payout_key, str(payout_value)),
                )
            conn.commit()
        finally:
            conn.close()
