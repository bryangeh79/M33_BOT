import sqlite3
import json

conn = sqlite3.connect("data/m33_lotto.db")
conn.row_factory = sqlite3.Row
cur = conn.cursor()

row = cur.execute("""
SELECT
    id,
    bet_type,
    bet_code,
    unit_value,
    numbers_json,
    regions_json,
    input_text,
    total,
    created_at
FROM bet_items
ORDER BY id DESC
LIMIT 1
""").fetchone()

if row is None:
    print("No bet_items found")
else:
    data = dict(row)
    print(data)
    print("numbers_json parsed =", json.loads(data["numbers_json"]) if data["numbers_json"] else None)
    print("regions_json parsed =", json.loads(data["regions_json"]) if data["regions_json"] else None)

conn.close()