import sqlite3

conn = sqlite3.connect("data/m33_lotto.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS settlement_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    draw_date TEXT NOT NULL,
    region_group TEXT NOT NULL,
    draw_result_id INTEGER,
    total_bets INTEGER NOT NULL DEFAULT 0,
    total_payout REAL NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'completed',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(draw_date, region_group)
)
""")

cur.execute("""
CREATE INDEX IF NOT EXISTS idx_settlement_runs_date_region
ON settlement_runs(draw_date, region_group)
""")

conn.commit()
conn.close()

print("✅ settlement_runs table ready")