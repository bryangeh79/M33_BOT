import os
import sqlite3
from pathlib import Path

ALLOWED_LANGS = {"en", "zh", "vi"}
DEFAULT_LANG = "en"


class UserPreferenceRepository:
    def __init__(self, db_path: str | Path | None = None):
        self.db_path = Path(db_path) if db_path else Path(os.getenv("DB_PATH", "data/m33_lotto.db"))

    def _get_connection(self) -> sqlite3.Connection:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def init_table(self) -> None:
        try:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS user_preferences (
                        user_id    TEXT NOT NULL PRIMARY KEY,
                        lang       TEXT NOT NULL DEFAULT 'en',
                        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
                conn.commit()
            finally:
                conn.close()
        except Exception:
            pass

    def get_lang(self, user_id: str) -> str:
        try:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT lang FROM user_preferences WHERE user_id = ? LIMIT 1",
                    (str(user_id),),
                )
                row = cursor.fetchone()
                if row:
                    lang = row["lang"]
                    return lang if lang in ALLOWED_LANGS else DEFAULT_LANG
                return DEFAULT_LANG
            finally:
                conn.close()
        except Exception:
            return DEFAULT_LANG

    def set_lang(self, user_id: str, lang: str) -> None:
        if lang not in ALLOWED_LANGS:
            return
        try:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO user_preferences (user_id, lang, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(user_id) DO UPDATE SET
                        lang       = excluded.lang,
                        updated_at = CURRENT_TIMESTAMP
                    """,
                    (str(user_id), lang),
                )
                conn.commit()
            finally:
                conn.close()
        except Exception:
            pass
