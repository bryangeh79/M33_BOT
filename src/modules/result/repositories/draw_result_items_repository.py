from src.app.database import get_db_path
import sqlite3
from datetime import datetime


class DrawResultItemsRepository:
    def __init__(self, db_path=None):
        self.db_path = db_path or get_db_path()

    def insert_items(self, draw_result_id, items):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            now = datetime.utcnow().isoformat(" ")
            rows = [
                (
                    draw_result_id,
                    item["sub_region_code"],
                    item["sub_region_name"],
                    item["prize_code"],
                    item["prize_order"],
                    item["item_order"],
                    item["number_value"],
                    now,
                )
                for item in items
            ]
            cursor.executemany(
                """
                INSERT INTO draw_result_items
                (
                    draw_result_id,
                    sub_region_code,
                    sub_region_name,
                    prize_code,
                    prize_order,
                    item_order,
                    number_value,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                rows,
            )
            conn.commit()

    def find_by_draw_result_id(self, draw_result_id):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT
                    sub_region_code,
                    sub_region_name,
                    prize_code,
                    prize_order,
                    item_order,
                    number_value
                FROM draw_result_items
                WHERE draw_result_id = ?
                ORDER BY prize_order, sub_region_code, item_order
                """,
                (draw_result_id,),
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def count_by_draw_result_id(self, draw_result_id) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM draw_result_items
                WHERE draw_result_id = ?
                """,
                (draw_result_id,),
            )
            row = cursor.fetchone()
            return int(row[0]) if row else 0

    def delete_by_draw_result_id(self, draw_result_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                DELETE FROM draw_result_items
                WHERE draw_result_id = ?
                """,
                (draw_result_id,),
            )
            conn.commit()
