import sqlite3

conn = sqlite3.connect("data/m33_lotto.db")
conn.row_factory = sqlite3.Row
cur = conn.cursor()

rows = cur.execute("""
SELECT id, draw_date, region_code, status, source_name, created_at
FROM draw_results
ORDER BY draw_date DESC, region_code ASC
LIMIT 30
""").fetchall()

for row in rows:
    print(dict(row))

conn.close()