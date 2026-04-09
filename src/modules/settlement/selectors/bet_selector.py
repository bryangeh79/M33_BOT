import json
import sqlite3

from src.app.database import DB_PATH


def _get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _safe_json_loads(value, default):
    if value is None:
        return default

    text = str(value).strip()
    if not text or text.lower() == "none":
        return default

    try:
        data = json.loads(text)
        if isinstance(data, list):
            return data
    except Exception:
        pass

    return default


def _safe_int_from_value(value, default=0):
    if value is None:
        return default

    text = str(value).strip()
    if not text or text.lower() == "none":
        return default

    try:
        return int(float(text))
    except Exception:
        return default


def _infer_numbers_from_input_text(input_text: str) -> list[str]:
    text = str(input_text or "").strip().lower()
    if not text:
        return []

    tokens = text.split()
    return [token for token in tokens if token.isdigit()]


def _infer_bet_code(bet_type: str, bet_code: str, number_mode: str, numbers: list[str]) -> str:
    normalized_bet_type = str(bet_type or "").strip().upper()
    normalized_bet_code = str(bet_code or "").strip().upper()
    normalized_number_mode = str(number_mode or "").strip().upper()

    if normalized_bet_code and normalized_bet_code != "NONE":
        return normalized_bet_code

    if normalized_number_mode and normalized_number_mode != "NONE":
        return normalized_number_mode

    if normalized_bet_type in {"DA", "DX", "DD"}:
        return "2C"

    if normalized_bet_type in {"LO", "XC"} and numbers:
        first_number = str(numbers[0]).strip()
        if first_number.isdigit():
            digits = len(first_number)
            if digits in (2, 3, 4):
                return f"{digits}C"

    return ""


def _normalize_bet_row(row: sqlite3.Row) -> dict:
    data = dict(row)

    bet_type = str(data.get("bet_type", "")).strip().upper()
    raw_bet_code = str(data.get("bet_code", "")).strip().upper()
    number_mode = str(data.get("number_mode", "")).strip().upper()

    numbers = _safe_json_loads(data.get("numbers_json"), [])
    regions = _safe_json_loads(data.get("regions_json"), [])

    if not numbers:
        numbers = _infer_numbers_from_input_text(data.get("input_text", ""))

    if not regions:
        raw_region_code = str(data.get("region_code", "")).strip()
        if raw_region_code and raw_region_code.lower() != "none":
            regions = [part.strip().lower() for part in raw_region_code.split(",") if part.strip()]

    unit = _safe_int_from_value(data.get("unit_value"), 0)
    if unit <= 0:
        unit = _safe_int_from_value(data.get("amount"), 0)

    bet_code = _infer_bet_code(
        bet_type=bet_type,
        bet_code=raw_bet_code,
        number_mode=number_mode,
        numbers=numbers,
    )

    return {
        "id": data["id"],
        "batch_id": data["batch_id"],
        "ticket_no": str(data.get("ticket_no", "")).strip().upper(),
        "region_group": str(data.get("region_group", "")).strip().upper(),
        "region_code": str(data.get("region_code", "")).strip(),
        "bet_type": bet_type,
        "bet_code": bet_code,
        "numbers": [str(x).strip() for x in numbers if str(x).strip()],
        "regions": [str(x).strip().lower() for x in regions if str(x).strip()],
        "unit": unit,
        "amount": str(data.get("amount", "")).strip(),
        "input_text": str(data.get("input_text", "")).strip(),
        "total": str(data.get("total", "")).strip(),
        "bet_date": str(data.get("bet_date", "")).strip(),
        "status": str(data.get("status", "")).strip().lower(),
        "created_at": str(data.get("created_at", "")).strip(),
    }


def get_bets_for_settlement(draw_date: str, region_group: str) -> list[dict]:
    """
    读取指定日期、指定区域组的 bet_items，
    转成 SettlementEngine 可直接使用的数据结构。
    """

    region_group = str(region_group).strip().upper()

    conn = _get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            bi.id,
            bi.batch_id,
            bi.ticket_no,
            bi.region_group,
            bi.region_code,
            bi.bet_type,
            bi.bet_code,
            bi.number_mode,
            bi.unit_value,
            bi.amount,
            bi.numbers_json,
            bi.regions_json,
            bi.input_text,
            bi.total,
            bi.status,
            bi.created_at,
            bb.bet_date
        FROM bet_items bi
        INNER JOIN bet_batches bb
            ON bb.id = bi.batch_id
        WHERE bb.bet_date = ?
          AND bi.region_group = ?
          AND bi.status = 'accepted'
          AND bb.status = 'accepted'
        ORDER BY bi.id ASC
        """,
        (draw_date, region_group),
    )

    rows = cursor.fetchall()
    conn.close()

    return [_normalize_bet_row(row) for row in rows]