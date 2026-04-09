import json
import sqlite3
from collections import OrderedDict
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
import re
from typing import Any

from src.i18n.translator import t

from src.modules.admin.services.admin_settings_service import AdminSettingsService
from src.modules.bet.parsers.bet_message_parser import parse_bet_message
from src.modules.bet.validators.bet_message_validator import validate_bet
from src.modules.bet.calculators.bet_total_calculator import calculate_total
from src.modules.bet.formatters.bet_success_formatter import format_success_response
from src.modules.bet.formatters.bet_error_formatter import format_error_response
from src.modules.bet.repositories.daily_counter_repository import (
    init_daily_counter_table,
    reserve_ticket_numbers,
)
from src.modules.customer.repositories.agent_customer_repository import AgentCustomerRepository

import os
SCHEMA_PATH = Path("src/data/schema/create_schema.sql")
admin_settings_service = AdminSettingsService()
agent_customer_repository = AgentCustomerRepository()
DEFAULT_AGENT_ID = AgentCustomerRepository.DEFAULT_AGENT_ID


def _get_db_path() -> Path:
    return Path(os.getenv("DB_PATH", "data/m33_lotto.db"))


def _today_iso_local() -> str:
    timezone_value = admin_settings_service.get_timezone()
    return datetime.now(timezone_value).date().isoformat()


def _get_connection():
    path_obj = _get_db_path()
    path_obj.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(str(path_obj))


def _column_exists(cursor, table_name: str, column_name: str) -> bool:
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    for col in columns:
        if len(col) > 1 and str(col[1]).lower() == column_name.lower():
            return True
    return False


def _ensure_soft_delete_columns(cursor) -> None:
    if not _column_exists(cursor, "bet_batches", "deleted_at"):
        cursor.execute("ALTER TABLE bet_batches ADD COLUMN deleted_at TEXT")

    if not _column_exists(cursor, "bet_items", "deleted_at"):
        cursor.execute("ALTER TABLE bet_items ADD COLUMN deleted_at TEXT")


def _ensure_settlement_bridge_columns(cursor) -> None:
    if not _column_exists(cursor, "bet_items", "bet_code"):
        cursor.execute("ALTER TABLE bet_items ADD COLUMN bet_code TEXT")

    if not _column_exists(cursor, "bet_items", "unit_value"):
        cursor.execute("ALTER TABLE bet_items ADD COLUMN unit_value TEXT")

    if not _column_exists(cursor, "bet_items", "numbers_json"):
        cursor.execute("ALTER TABLE bet_items ADD COLUMN numbers_json TEXT")

    if not _column_exists(cursor, "bet_items", "regions_json"):
        cursor.execute("ALTER TABLE bet_items ADD COLUMN regions_json TEXT")


def _ensure_customer_batch_columns(cursor) -> None:
    if not _column_exists(cursor, "bet_batches", "customer_code"):
        cursor.execute("ALTER TABLE bet_batches ADD COLUMN customer_code TEXT")

    if not _column_exists(cursor, "bet_batches", "customer_commission_rate_snapshot"):
        cursor.execute("ALTER TABLE bet_batches ADD COLUMN customer_commission_rate_snapshot TEXT")


def init_database():
    conn = _get_connection()
    cursor = conn.cursor()

    if SCHEMA_PATH.exists():
        schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
        cursor.executescript(schema_sql)

    _ensure_soft_delete_columns(cursor)
    _ensure_settlement_bridge_columns(cursor)
    _ensure_customer_batch_columns(cursor)

    conn.commit()
    conn.close()

    init_daily_counter_table()


def _number_mode_from_result(result: dict) -> str:
    bet_type = result.get("type")

    if bet_type in {"da", "dx"}:
        return "2c"

    number = str(result.get("number", ""))
    return f"{len(number)}c"


def _bet_code_from_result(result: dict) -> str:
    return _number_mode_from_result(result).upper()


def _format_decimal(value: Decimal) -> str:
    if value == value.to_integral():
        return str(int(value))
    return format(value.normalize(), "f").rstrip("0").rstrip(".")


def _region_code_from_result(result: dict) -> str:
    if result.get("type") == "dx":
        return ",".join(result.get("prefixes", []))
    return str(result.get("prefix", ""))


def _numbers_from_result(result: dict) -> list[str]:
    numbers = result.get("numbers")
    if isinstance(numbers, list) and numbers:
        return [str(x).strip() for x in numbers if str(x).strip()]

    number = str(result.get("number", "")).strip()
    return [number] if number else []


def _regions_from_result(result: dict) -> list[str]:
    prefixes = result.get("prefixes")
    if isinstance(prefixes, list) and prefixes:
        return [str(x).strip().lower() for x in prefixes if str(x).strip()]

    prefix = str(result.get("prefix", "")).strip().lower()
    return [prefix] if prefix else []


def _safe_list(value) -> list[str]:
    if isinstance(value, list):
        return [str(x).strip() for x in value if str(x).strip()]
    return []


def _to_decimal(value: Any) -> Decimal:
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value).strip())
    except Exception:
        return Decimal("0")


def _is_dx_result(result: dict) -> bool:
    if str(result.get("type", "")).strip().lower() == "dx":
        return True

    regions = _regions_from_result(result)
    return len(regions) > 1


def _over_limit_local_key(result: dict) -> str:
    bet_type = str(result.get("type", "")).strip().lower()
    number_mode = _number_mode_from_result(result).upper()

    if bet_type == "lo":
        return f"{number_mode}_LO"
    if bet_type == "dd":
        return "2C_DD"
    if bet_type == "da":
        return "2C_DA"
    if bet_type == "dx":
        return "2C_DX"
    if bet_type == "xc":
        return f"{number_mode}_XC"

    return "UNKNOWN"


def _over_limit_scope_key(result: dict) -> tuple[str, ...]:
    bet_type = str(result.get("type", "")).strip().lower()
    numbers = _numbers_from_result(result)
    regions = [r.lower() for r in _regions_from_result(result)]

    if bet_type == "da":
        return tuple(sorted(numbers))
    if _is_dx_result(result):
        return tuple(sorted(regions) + sorted(numbers))

    first_number = numbers[0] if numbers else ""
    first_region = regions[0] if regions else ""
    return (first_region, first_number)


def _load_existing_exposure(target_date: str, region_group: str) -> dict[tuple[str, str, tuple[str, ...]], Decimal]:
    conn = _get_connection()
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                region_code,
                bet_type,
                number_mode,
                amount,
                numbers_json,
                regions_json
            FROM bet_items bi
            INNER JOIN bet_batches bb
                ON bb.id = bi.batch_id
            WHERE bb.bet_date = ?
              AND bb.region_group = ?
              AND bb.status = 'accepted'
              AND bi.status = 'accepted'
            """,
            (target_date, region_group),
        )
        rows = cursor.fetchall()
    finally:
        conn.close()

    exposure: dict[tuple[str, str, tuple[str, ...]], Decimal] = {}

    for row in rows:
        bet_type = str(row["bet_type"] or "").strip().lower()
        number_mode = str(row["number_mode"] or "").strip().upper()
        local_key = _over_limit_local_key({"type": bet_type, "number_mode": number_mode, "number": "00" if number_mode == "2C" else "000"})

        try:
            numbers = json.loads(row["numbers_json"]) if row["numbers_json"] else []
        except Exception:
            numbers = []
        if not isinstance(numbers, list):
            numbers = []
        numbers = [str(x).strip() for x in numbers if str(x).strip()]

        try:
            regions = json.loads(row["regions_json"]) if row["regions_json"] else []
        except Exception:
            regions = []
        if not isinstance(regions, list):
            regions = []
        regions = [str(x).strip().lower() for x in regions if str(x).strip()]
        if not regions:
            raw_region = str(row["region_code"] or "").strip().lower()
            regions = [part.strip() for part in raw_region.split(",") if part.strip()]

        fake_result = {
            "type": bet_type,
            "number_mode": number_mode.lower(),
            "numbers": numbers,
            "number": numbers[0] if numbers else "",
            "prefixes": regions,
            "prefix": regions[0] if regions else "",
        }
        local_key = _over_limit_local_key(fake_result)
        scope_key = _over_limit_scope_key(fake_result)
        exposure[(region_group, local_key, scope_key)] = exposure.get(
            (region_group, local_key, scope_key), Decimal("0")
        ) + _to_decimal(row["amount"])

    return exposure


def _check_over_limit(target_date: str, region_group: str, calculated_results: list[dict]) -> dict[str, Any]:
    exposure = _load_existing_exposure(target_date, region_group)
    violations: list[dict[str, Any]] = []

    for result in calculated_results:
        local_key = _over_limit_local_key(result)
        if local_key == "UNKNOWN":
            continue

        scope_key = _over_limit_scope_key(result)
        current_amount = exposure.get((region_group, local_key, scope_key), Decimal("0"))
        new_amount = _to_decimal(result.get("amount"))
        next_amount = current_amount + new_amount
        limit_amount = _to_decimal(admin_settings_service.get_limit_value(region_group, local_key))

        if next_amount > limit_amount:
            violations.append(
                {
                    "input_text": str(result.get("raw_input", "")).strip(),
                    "bet_type": str(result.get("type", "")).upper(),
                    "scope_key": scope_key,
                    "current_amount": current_amount,
                    "new_amount": new_amount,
                    "next_amount": next_amount,
                    "limit_amount": limit_amount,
                    "local_key": local_key,
                }
            )

        exposure[(region_group, local_key, scope_key)] = next_amount

    return {
        "has_over_limit": len(violations) > 0,
        "violations": violations,
        "action": admin_settings_service.get_over_limit_action(),
        "notify_customer": admin_settings_service.is_customer_notification_enabled(),
    }


def _build_over_limit_notification(check_result: dict[str, Any], accepted: bool, lang: str = "en") -> str:
    if not check_result.get("notify_customer"):
        return ""

    header = (
        t("BET_OVER_LIMIT_ACCEPT", lang)
        if accepted
        else t("BET_OVER_LIMIT_REJECT", lang)
    )

    violation = (check_result.get("violations") or [{}])[0]
    input_text = str(violation.get("input_text", "")).strip()

    details = []
    if input_text:
        details.append(t("BET_OVER_LIMIT_INPUT", lang, value=input_text))

    return header + ("\n" + "\n".join(details) if details else "")


def _is_same_day_target(target_date: str) -> bool:
    timezone = admin_settings_service.get_timezone()
    return str(target_date).strip() == datetime.now(timezone).date().isoformat()


def _check_cutoff_time(target_date: str, region_group: str) -> dict[str, Any]:
    if not _is_same_day_target(target_date):
        return {"is_closed": False, "cutoff_time": None}

    normalized_region = str(region_group).upper().strip()
    timezone = admin_settings_service.get_timezone()
    now_local = datetime.now(timezone)
    cutoff_time = admin_settings_service.get_cutoff_time(normalized_region)
    cutoff_hour, cutoff_minute = [int(part) for part in cutoff_time.split(":", 1)]
    cutoff_dt = now_local.replace(
        hour=cutoff_hour,
        minute=cutoff_minute,
        second=0,
        microsecond=0,
    )

    return {
        "is_closed": now_local > cutoff_dt,
        "cutoff_time": cutoff_time,
        "region_group": normalized_region,
    }


def _format_cutoff_display(value: str) -> str:
    parsed = datetime.strptime(value, "%H:%M")
    return parsed.strftime("%I:%M %p").lstrip("0")


def _build_cutoff_closed_message(region_group: str, cutoff_time: str, lang: str = "en") -> str:
    return "\n".join(
        [
            t("BET_CUTOFF_CLOSED", lang),
            t("BET_CUTOFF_REGION_TIME", lang, region=str(region_group).upper(), time=_format_cutoff_display(cutoff_time)),
        ]
    )


def _should_bypass_history_validation(error_code: str | None) -> bool:
    return error_code == "SCHEDULE_CLOSED"


def _prepend_test_mode_notice(response_text: str) -> str:
    notice = t("BET_TEST_MODE_NOTICE")
    body = str(response_text or "").strip()
    if not body:
        return notice
    return f"{notice}\n\n{body}"


CUSTOMER_CODE_PATTERN = re.compile(r"^c(\d{1,2})$", re.IGNORECASE)
UNASSIGNED_CUSTOMER_CODE = "UNASSIGNED"
DEFAULT_CUSTOMER_COMMISSION_RATE = Decimal("0")


def _normalize_customer_code(value: str) -> str | None:
    match = CUSTOMER_CODE_PATTERN.match(str(value).strip())
    if not match:
        return None
    return f"C{int(match.group(1)):02d}"


def _extract_customer_context(text: str) -> tuple[str, str]:
    normalized_text = str(text or "").replace("\r\n", "\n").replace("\r", "\n").strip()
    if not normalized_text:
        return UNASSIGNED_CUSTOMER_CODE, ""

    raw_lines = [line.strip() for line in normalized_text.split("\n") if line.strip()]
    if not raw_lines:
        return UNASSIGNED_CUSTOMER_CODE, ""

    customer_code = _normalize_customer_code(raw_lines[0])
    if customer_code:
        bet_text = "\n".join(raw_lines[1:]).strip()
        return customer_code, bet_text

    return UNASSIGNED_CUSTOMER_CODE, normalized_text


def _resolve_customer_commission_rate_snapshot(customer_code: str) -> Decimal:
    normalized_code = str(customer_code).strip().upper()
    if not normalized_code or normalized_code == UNASSIGNED_CUSTOMER_CODE:
        return DEFAULT_CUSTOMER_COMMISSION_RATE

    row = agent_customer_repository.get_by_agent_and_code(DEFAULT_AGENT_ID, normalized_code)
    if not row:
        return DEFAULT_CUSTOMER_COMMISSION_RATE

    return _to_decimal(row["customer_commission_rate"])


def _group_results_for_success_display(calculated_results: list[dict]) -> list[dict]:
    """
    按“区域 + 原始号码组 + mode + amount”重新组合成功回执显示。
    数据库存储仍保持拆分结果，不受影响。
    """
    grouped: OrderedDict[tuple, dict] = OrderedDict()

    for result in calculated_results:
        bet_type = str(result.get("type", "")).lower().strip()

        if bet_type == "dx":
            region_label = ",".join(
                str(x).strip().upper()
                for x in result.get("prefixes", [])
                if str(x).strip()
            )
        else:
            region_label = str(result.get("prefix", "")).strip().upper()

        if not region_label:
            region_label = "-"

        group_numbers = _safe_list(result.get("group_numbers"))
        if not group_numbers:
            group_numbers = _numbers_from_result(result)

        numbers_str = " ".join(group_numbers) if group_numbers else "-"
        display_mode = str(result.get("display_mode", "")).strip().upper()
        amount_value = result.get("amount", Decimal("0"))
        amount_text = _format_decimal(amount_value)

        key = (region_label, numbers_str, display_mode, amount_text)

        if key not in grouped:
            grouped[key] = {
                "region_label": region_label,
                "numbers": group_numbers,
                "numbers_str": numbers_str,
                "display_mode": display_mode or "-",
                "amount": amount_value,
                "total": Decimal("0"),
                "type": bet_type,
                "prefix": str(result.get("prefix", "")).strip().lower(),
                "prefixes": result.get("prefixes", []),
            }

        grouped[key]["total"] += result.get("total", Decimal("0"))

    return list(grouped.values())


def process_bet_message(
    user_id: str,
    region_group: str,
    text: str,
    target_date: str,
    allow_history_bet_override: bool = False,
    lang: str = "en",
):
    region_group = region_group.upper()
    init_database()

    customer_code, bet_text = _extract_customer_context(text)
    customer_commission_rate_snapshot = _resolve_customer_commission_rate_snapshot(customer_code)

    parsed_bets = parse_bet_message(bet_text, region_group)

    if not parsed_bets:
        return False, format_error_response([t("BET_INVALID_INPUT", lang)], lang=lang)

    error_lines = []
    seen_errors = set()

    for parsed_bet in parsed_bets:
        valid, error_code, _ = validate_bet(parsed_bet, region_group, target_date=target_date)

        if (not valid) and allow_history_bet_override and _should_bypass_history_validation(error_code):
            valid = True
            error_code = None

        if not valid:
            raw_input = parsed_bet.get(
                "source_line",
                parsed_bet.get("raw_input", t("BET_INVALID_INPUT", lang)),
            )

            if error_code == "SCHEDULE_CLOSED":
                error_line = f"{raw_input} {t('BET_SCHEDULE_CLOSED', lang)}"
            else:
                error_line = f"{raw_input} {t('BET_INVALID_INPUT', lang)}"

            if error_line not in seen_errors:
                seen_errors.add(error_line)
                error_lines.append(error_line)

    if error_lines:
        return False, format_error_response(error_lines, lang=lang)

    calculated_results = []
    for parsed_bet in parsed_bets:
        calculated = calculate_total(parsed_bet, region_group)

        calculated["source_line"] = parsed_bet.get(
            "source_line",
            parsed_bet.get("raw_input", calculated.get("raw_input", "")),
        )
        calculated["display_raw_input"] = parsed_bet.get(
            "display_raw_input",
            parsed_bet.get("source_line", parsed_bet.get("raw_input", "")),
        )
        calculated["group_numbers"] = _safe_list(parsed_bet.get("group_numbers"))
        calculated["display_mode"] = str(parsed_bet.get("display_mode", "")).strip().upper()

        if not calculated.get("prefix") and parsed_bet.get("prefix"):
            calculated["prefix"] = parsed_bet.get("prefix")

        if not calculated.get("prefixes") and parsed_bet.get("prefixes"):
            calculated["prefixes"] = parsed_bet.get("prefixes")

        if not calculated.get("type") and parsed_bet.get("type"):
            calculated["type"] = parsed_bet.get("type")

        calculated_results.append(calculated)

    cutoff_check = _check_cutoff_time(target_date, region_group)
    if cutoff_check["is_closed"]:
        return False, _build_cutoff_closed_message(region_group, cutoff_check["cutoff_time"], lang=lang)

    over_limit_check = _check_over_limit(target_date, region_group, calculated_results)
    if over_limit_check["has_over_limit"] and over_limit_check["action"] == admin_settings_service.RISK_ACTION_REJECT:
        return False, _build_over_limit_notification(over_limit_check, accepted=False, lang=lang)

    ticket_numbers = reserve_ticket_numbers(region_group, 1, target_date=target_date)
    ticket_no = ticket_numbers[0]

    batch_total = sum(result["total"] for result in calculated_results)
    today = _today_iso_local()
    batch_code = f"{region_group}-{target_date}-{ticket_no}"

    conn = _get_connection()

    try:
        cursor = conn.cursor()
        cursor.execute("BEGIN")

        cursor.execute(
            """
            INSERT INTO bet_batches (
                batch_code,
                user_id,
                region_group,
                input_date,
                bet_date,
                raw_input,
                line_count,
                batch_total,
                status,
                customer_code,
                customer_commission_rate_snapshot
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                batch_code,
                str(user_id),
                region_group,
                today,
                target_date,
                text.strip(),
                len(calculated_results),
                _format_decimal(batch_total),
                "accepted",
                customer_code,
                _format_decimal(customer_commission_rate_snapshot),
            ),
        )

        batch_id = cursor.lastrowid

        for index, result in enumerate(calculated_results, start=1):
            numbers = _numbers_from_result(result)
            regions = _regions_from_result(result)

            cursor.execute(
                """
                INSERT INTO bet_items (
                    batch_id,
                    sequence_no,
                    ticket_no,
                    region_group,
                    region_code,
                    bet_type,
                    bet_code,
                    number_mode,
                    amount,
                    unit_value,
                    numbers_json,
                    regions_json,
                    input_text,
                    total,
                    status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    batch_id,
                    index,
                    ticket_no,
                    region_group,
                    _region_code_from_result(result),
                    result["type"],
                    _bet_code_from_result(result),
                    _number_mode_from_result(result),
                    _format_decimal(result["amount"]),
                    _format_decimal(result["amount"]),
                    json.dumps(numbers, ensure_ascii=False),
                    json.dumps(regions, ensure_ascii=False),
                    result["raw_input"],
                    _format_decimal(result["total"]),
                    "accepted",
                ),
            )

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

    display_results = _group_results_for_success_display(calculated_results)

    response_text = format_success_response(
        region_group,
        [ticket_no],
        display_results,
        target_date=target_date,
        lang=lang,
    )

    if over_limit_check["has_over_limit"]:
        notice = _build_over_limit_notification(over_limit_check, accepted=True, lang=lang)
        if notice:
            response_text = f"{response_text}\n\n{notice}"

    if allow_history_bet_override:
        response_text = _prepend_test_mode_notice(response_text)

    return True, response_text


def delete_ticket(ticket_no: str, target_date: str, lang: str = "en"):
    init_database()

    ticket_no = str(ticket_no).strip().upper()
    today_iso = _today_iso_local()

    conn = _get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT
                bb.id,
                bb.status,
                bb.region_group
            FROM bet_batches bb
            INNER JOIN bet_items bi
                ON bi.batch_id = bb.id
            WHERE bb.bet_date = ?
              AND bi.ticket_no = ?
            ORDER BY bb.id DESC
            LIMIT 1
            """,
            (target_date, ticket_no),
        )

        row = cursor.fetchone()

        if not row:
            if target_date == today_iso:
                return False, t("BET_DELETE_NOT_FOUND", lang, ticket_no=ticket_no)
            return False, t("BET_DELETE_NOT_FOUND_WITH_DATE", lang, ticket_no=ticket_no, date=target_date)

        batch_id, batch_status, region_group = row

        if str(batch_status).lower() == "deleted":
            if target_date == today_iso:
                return False, t("BET_DELETE_ALREADY_DELETED", lang, ticket_no=ticket_no)
            return False, t("BET_DELETE_ALREADY_DELETED_WITH_DATE", lang, ticket_no=ticket_no, date=target_date)

        cursor.execute("BEGIN")

        cursor.execute(
            """
            UPDATE bet_batches
            SET status = 'deleted',
                deleted_at = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (batch_id,),
        )

        cursor.execute(
            """
            UPDATE bet_items
            SET status = 'deleted',
                deleted_at = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            WHERE batch_id = ?
            """,
            (batch_id,),
        )

        conn.commit()

        if target_date == today_iso:
            return True, t("BET_DELETE_SUCCESS", lang, region=region_group, ticket_no=ticket_no)

        return True, t("BET_DELETE_SUCCESS_WITH_DATE", lang, region=region_group, ticket_no=ticket_no, date=target_date)

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()
