import os
import sqlite3
from pathlib import Path
from typing import Any

DB_PATH = os.getenv("DB_PATH", "data/m33_lotto.db")


class AdminUserRepository:
    def __init__(self, db_path: str | Path | None = None):
        if db_path:
            self.db_path = Path(db_path)
        else:
            self.db_path = Path(DB_PATH)

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
                CREATE TABLE IF NOT EXISTS admin_users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL UNIQUE,
                    username TEXT,
                    role TEXT NOT NULL DEFAULT 'USER',
                    is_active INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.commit()
        finally:
            conn.close()

    def get_user_by_id(self, user_id: str) -> dict[str, Any] | None:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT *
                FROM admin_users
                WHERE user_id = ?
                LIMIT 1
                """,
                (str(user_id),),
            )
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def upsert_admin(self, user_id: str, username: str | None = None) -> None:
        user_id = str(user_id).strip()
        username = (username or '').strip() or None

        existing = self.get_user_by_id(user_id)

        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            if existing:
                if username:
                    cursor.execute(
                        """
                        UPDATE admin_users
                        SET username = ?,
                            role = 'ADMIN',
                            is_active = 1,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE user_id = ?
                        """,
                        (username, user_id),
                    )
                else:
                    cursor.execute(
                        """
                        UPDATE admin_users
                        SET role = 'ADMIN',
                            is_active = 1,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE user_id = ?
                        """,
                        (user_id,),
                    )
            else:
                cursor.execute(
                    """
                    INSERT INTO admin_users (
                        user_id,
                        username,
                        role,
                        is_active
                    )
                    VALUES (?, ?, 'ADMIN', 1)
                    """,
                    (user_id, username),
                )
            conn.commit()
        finally:
            conn.close()

    def demote_to_user(self, user_id: str) -> None:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE admin_users
                SET role = 'USER',
                    is_active = 1,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
                """,
                (str(user_id).strip(),),
            )
            conn.commit()
        finally:
            conn.close()

    def list_active_admins(self) -> list[dict[str, Any]]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT *
                FROM admin_users
                WHERE role = 'ADMIN'
                  AND is_active = 1
                ORDER BY created_at ASC, id ASC
                """
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()
