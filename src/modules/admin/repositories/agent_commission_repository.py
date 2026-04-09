import os
import sqlite3
from pathlib import Path

from src.app.database import get_db_path

class AgentCommissionRepository:
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
                CREATE TABLE IF NOT EXISTS agent_commission_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    commission_rate TEXT NOT NULL DEFAULT '0',
                    is_active INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.commit()
        finally:
            conn.close()

    def ensure_default(self, default_rate: str = '0') -> None:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id
                FROM agent_commission_settings
                WHERE is_active = 1
                ORDER BY id DESC
                LIMIT 1
                """
            )
            if not cursor.fetchone():
                cursor.execute(
                    """
                    INSERT INTO agent_commission_settings (commission_rate, is_active)
                    VALUES (?, 1)
                    """,
                    (str(default_rate),),
                )
                conn.commit()
        finally:
            conn.close()

    def get_current_rate(self) -> str:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT commission_rate
                FROM agent_commission_settings
                WHERE is_active = 1
                ORDER BY id DESC
                LIMIT 1
                """
            )
            row = cursor.fetchone()
            return str(row['commission_rate']) if row else '0'
        finally:
            conn.close()

    def set_rate(self, rate: str) -> None:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE agent_commission_settings SET is_active = 0 WHERE is_active = 1")
            cursor.execute(
                """
                INSERT INTO agent_commission_settings (commission_rate, is_active)
                VALUES (?, 1)
                """,
                (str(rate),),
            )
            conn.commit()
        finally:
            conn.close()
