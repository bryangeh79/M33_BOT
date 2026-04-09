import os
import sqlite3
from pathlib import Path

from src.app.database import get_db_path

class RiskControlRepository:
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
                CREATE TABLE IF NOT EXISTS risk_control_settings (
                    setting_key TEXT PRIMARY KEY,
                    setting_value TEXT NOT NULL,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.commit()
        finally:
            conn.close()

    def ensure_default(self, setting_key: str, setting_value: str) -> None:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO risk_control_settings (setting_key, setting_value)
                VALUES (?, ?)
                ON CONFLICT(setting_key) DO NOTHING
                """,
                (str(setting_key), str(setting_value)),
            )
            conn.commit()
        finally:
            conn.close()

    def get(self, setting_key: str, default: str | None = None) -> str | None:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT setting_value
                FROM risk_control_settings
                WHERE setting_key = ?
                LIMIT 1
                """,
                (str(setting_key),),
            )
            row = cursor.fetchone()
            return str(row['setting_value']) if row else default
        finally:
            conn.close()

    def set(self, setting_key: str, setting_value: str) -> None:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO risk_control_settings (setting_key, setting_value)
                VALUES (?, ?)
                ON CONFLICT(setting_key) DO UPDATE SET
                    setting_value = excluded.setting_value,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (str(setting_key), str(setting_value)),
            )
            conn.commit()
        finally:
            conn.close()
