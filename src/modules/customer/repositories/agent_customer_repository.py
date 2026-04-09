import os
import sqlite3
from pathlib import Path

class AgentCustomerRepository:
    DEFAULT_AGENT_ID = "DEFAULT"

    def __init__(self, db_path: str | Path | None = None):
        self.db_path = Path(db_path) if db_path else Path(os.getenv("DB_PATH", "data/m33_lotto.db"))

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
                CREATE TABLE IF NOT EXISTS agent_customers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id TEXT NOT NULL,
                    customer_code TEXT NOT NULL,
                    customer_name TEXT,
                    customer_commission_rate TEXT NOT NULL DEFAULT '0',
                    customer_bonus_plan TEXT NOT NULL DEFAULT 'DEFAULT',
                    status TEXT NOT NULL DEFAULT 'active',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(agent_id, customer_code)
                )
                """
            )
            cursor.execute("PRAGMA table_info(agent_customers)")
            columns = {row[1] for row in cursor.fetchall()}
            if "customer_bonus_plan" not in columns:
                cursor.execute(
                    "ALTER TABLE agent_customers ADD COLUMN customer_bonus_plan TEXT NOT NULL DEFAULT 'DEFAULT'"
                )
            conn.commit()
        finally:
            conn.close()

    def get_by_agent_and_code(self, agent_id: str, customer_code: str):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT *
                FROM agent_customers
                WHERE agent_id = ?
                  AND customer_code = ?
                  AND status = 'active'
                LIMIT 1
                """,
                (str(agent_id).strip(), str(customer_code).strip().upper()),
            )
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def upsert_customer(
        self,
        agent_id: str,
        customer_code: str,
        customer_name: str = "",
        customer_commission_rate: str = "0",
        customer_bonus_plan: str = "DEFAULT",
    ) -> None:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO agent_customers
                (
                    agent_id,
                    customer_code,
                    customer_name,
                    customer_commission_rate,
                    customer_bonus_plan,
                    status,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                ON CONFLICT(agent_id, customer_code)
                DO UPDATE SET
                    customer_name = excluded.customer_name,
                    customer_commission_rate = excluded.customer_commission_rate,
                    customer_bonus_plan = excluded.customer_bonus_plan,
                    status = 'active',
                    updated_at = CURRENT_TIMESTAMP
                """,
                (
                    str(agent_id).strip(),
                    str(customer_code).strip().upper(),
                    str(customer_name).strip(),
                    str(customer_commission_rate).strip(),
                    str(customer_bonus_plan).strip() or "DEFAULT",
                ),
            )
            conn.commit()
        finally:
            conn.close()

    def deactivate_customer(self, agent_id: str, customer_code: str) -> bool:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE agent_customers
                SET status = 'inactive',
                    updated_at = CURRENT_TIMESTAMP
                WHERE agent_id = ?
                  AND customer_code = ?
                  AND status = 'active'
                """,
                (str(agent_id).strip(), str(customer_code).strip().upper()),
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def list_active_customers(self, agent_id: str | None = None) -> list[dict]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            if agent_id:
                cursor.execute(
                    """
                    SELECT *
                    FROM agent_customers
                    WHERE agent_id = ?
                      AND status = 'active'
                    ORDER BY customer_code ASC
                    """,
                    (str(agent_id).strip(),),
                )
            else:
                cursor.execute(
                    """
                    SELECT *
                    FROM agent_customers
                    WHERE status = 'active'
                    ORDER BY agent_id ASC, customer_code ASC
                    """
                )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()
