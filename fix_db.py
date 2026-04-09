import sqlite3

conn = sqlite3.connect("data/m33_lotto.db")
cur = conn.cursor()

# 查看当前列
columns = [row[1] for row in cur.execute("PRAGMA table_info(bet_items)").fetchall()]
print("Existing columns:", columns)

def add_column(name, sql):
    if name not in columns:
        print(f"Adding column: {name}")
        cur.execute(sql)
    else:
        print(f"Column already exists: {name}")

add_column("bet_code", "ALTER TABLE bet_items ADD COLUMN bet_code TEXT")
add_column("unit_value", "ALTER TABLE bet_items ADD COLUMN unit_value TEXT")
add_column("numbers_json", "ALTER TABLE bet_items ADD COLUMN numbers_json TEXT")
add_column("regions_json", "ALTER TABLE bet_items ADD COLUMN regions_json TEXT")

conn.commit()

# 再检查一次
columns = [row[1] for row in cur.execute("PRAGMA table_info(bet_items)").fetchall()]
print("Updated columns:", columns)

conn.close()
print("✅ Migration DONE")