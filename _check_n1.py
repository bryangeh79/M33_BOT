import sqlite3

conn = sqlite3.connect(r"data\m33_lotto.db")
conn.row_factory = sqlite3.Row
cur = conn.cursor()

sql = "SELECT sr.id, sr.bet_id, sr.region, sr.bet_type, sr.payout, sr.win_details " \
      "FROM settlement_results sr " \
      "INNER JOIN bet_items bi ON bi.id = sr.bet_id " \
      "INNER JOIN bet_batches bb ON bb.id = bi.batch_id " \
      "WHERE bi.ticket_no = 'N1' " \
      "AND bb.bet_date = '2026-03-31' " \
      "ORDER BY sr.id ASC"

cur.execute(sql)
rows = cur.fetchall()

print("rows =", len(rows))
for r in rows:
    d = dict(r)
    print("=" * 80)
    for k, v in d.items():
        print(f"{k}: {v}")
