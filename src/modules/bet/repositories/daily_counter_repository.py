import os
import sqlite3
from datetime import date
from pathlib import Path


def _get_db_path() -> Path:
    return Path(os.getenv("DB_PATH", "data/m33_lotto.db"))


def _get_connection():
    db_path = _get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(str(db_path))


def init_daily_counter_table():
    conn = _get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_counters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            counter_date TEXT NOT NULL,
            region_group TEXT NOT NULL,
            last_counter INTEGER NOT NULL DEFAULT 0,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(counter_date, region_group)
        )
    """)

    conn.commit()
    conn.close()


def reserve_ticket_numbers(region_group: str, count: int, target_date: str | None = None) -> list[str]:
    """
    按 bet_date + region_group 发号
    例如：
    - 2026-03-20 + MN -> N1, N2, N3
    - 2026-03-21 + MN -> N1, N2, N3（重新开始）
    """

    if count <= 0:
        return []

    region_group = region_group.upper()
    counter_date = target_date or date.today().isoformat()

    prefix_map = {
        "MN": "N",
        "MT": "T",
        "MB": "B",
    }

    if region_group not in prefix_map:
        raise ValueError("Invalid region group")

    prefix = prefix_map[region_group]

    conn = _get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO daily_counters (counter_date, region_group, last_counter)
        VALUES (?, ?, 0)
    """, (counter_date, region_group))

    cursor.execute("""
        SELECT last_counter
        FROM daily_counters
        WHERE counter_date = ? AND region_group = ?
    """, (counter_date, region_group))

    row = cursor.fetchone()
    last_counter = row[0] if row else 0

    start = last_counter + 1
    end = last_counter + count

    cursor.execute("""
        UPDATE daily_counters
        SET last_counter = ?, updated_at = CURRENT_TIMESTAMP
        WHERE counter_date = ? AND region_group = ?
    """, (end, counter_date, region_group))

    conn.commit()
    conn.close()

    return [f"{prefix}{i}" for i in range(start, end + 1)]
