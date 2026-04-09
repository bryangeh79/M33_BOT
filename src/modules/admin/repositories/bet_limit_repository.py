import os
import sqlite3
from pathlib import Path

DB_PATH = os.getenv("DB_PATH", "data/m33_lotto.db")


class BetLimitRepository:
    def __init__(self, db_path: str | Path | None = None):
        self.db_path = Path(db_path) if db_path else Path(DB_PATH)

    def _get_connection(self) -> sqlite3.Connection:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def init_table(self) -> None:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS bet_limit_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    limit_key TEXT NOT NULL UNIQUE,
                    limit_amount TEXT NOT NULL DEFAULT '100',
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
            for limit_key, limit_amount in defaults.items():
                cursor.execute(
                    """
                    INSERT INTO bet_limit_settings (limit_key, limit_amount, is_active)
                    VALUES (?, ?, 1)
                    ON CONFLICT(limit_key) DO NOTHING
                    """,
                    (limit_key, str(limit_amount)),
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
                SELECT limit_key, limit_amount
                FROM bet_limit_settings
                WHERE is_active = 1
                ORDER BY limit_key ASC
                """
            )
            rows = cursor.fetchall()
            return {str(row['limit_key']): str(row['limit_amount']) for row in rows}
        finally:
            conn.close()

    def upsert_many(self, values: dict[str, str]) -> None:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            for limit_key, limit_amount in values.items():
                cursor.execute(
                    """
                    INSERT INTO bet_limit_settings (limit_key, limit_amount, is_active)
                    VALUES (?, ?, 1)
                    ON CONFLICT(limit_key) DO UPDATE SET
                        limit_amount = excluded.limit_amount,
                        is_active = 1,
                        updated_at = CURRENT_TIMESTAMP
                    """,
                    (limit_key, str(limit_amount)),
                )
            conn.commit()
        finally:
            conn.close()
