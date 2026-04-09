from src.app.database import get_db_path
import sqlite3
from datetime import datetime


class DrawResultsRepository:
    def __init__(self, db_path=None):
        self.db_path = db_path

    def _get_db_path(self):
        return self.db_path or get_db_path()

    def get_result(self, draw_date, region_code):
        with sqlite3.connect(self._get_db_path()) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT
                    id,
                    draw_date,
                    region_code,
                    source_name,
                    source_url,
                    status,
                    fetched_at,
                    created_at,
                    updated_at
                FROM draw_results
                WHERE draw_date = ? AND region_code = ?
                """,
                (draw_date, region_code),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return dict(row)

    def insert_result(
        self,
        draw_date,
        region_code,
        source_name,
        source_url,
        status,
        fetched_at,
    ):
        with sqlite3.connect(self._get_db_path()) as conn:
            cursor = conn.cursor()
            now = datetime.utcnow().isoformat(" ")
            cursor.execute(
                """
                INSERT INTO draw_results
                (
                    draw_date,
                    region_code,
                    source_name,
                    source_url,
                    status,
                    fetched_at,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    draw_date,
                    region_code,
                    source_name,
                    source_url,
                    status,
                    fetched_at,
                    now,
                    now,
                ),
            )
            conn.commit()
            return cursor.lastrowid

    def update_result_status(self, draw_result_id, status, fetched_at):
        with sqlite3.connect(self._get_db_path()) as conn:
            cursor = conn.cursor()
            now = datetime.utcnow().isoformat(" ")
            cursor.execute(
                """
                UPDATE draw_results
                SET status = ?, fetched_at = ?, updated_at = ?
                WHERE id = ?
                """,
                (status, fetched_at, now, draw_result_id),
            )
            conn.commit()

    def update_result_record(
        self,
        draw_result_id,
        status,
        fetched_at,
        source_name,
        source_url,
    ):
        with sqlite3.connect(self._get_db_path()) as conn:
            cursor = conn.cursor()
            now = datetime.utcnow().isoformat(" ")
            cursor.execute(
                """
                UPDATE draw_results
                SET
                    status = ?,
                    fetched_at = ?,
                    source_name = ?,
                    source_url = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (status, fetched_at, source_name, source_url, now, draw_result_id),
            )
            conn.commit()

    def exists(self, draw_date, region_code):
        with sqlite3.connect(self._get_db_path()) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT 1
                FROM draw_results
                WHERE draw_date = ? AND region_code = ?
                """,
                (draw_date, region_code),
            )
            return cursor.fetchone() is not None
