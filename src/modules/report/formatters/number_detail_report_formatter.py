from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from src.i18n.translator import t
from src.modules.report.constants.report_constants import REPORT_REGION_GROUPS
from src.modules.report.helpers.report_normalizer import ReportNormalizer


SECTION_ORDER = [
    ("2C", ["LO", "DD", "DA", "DX"]),
    ("3C", ["LO", "XC"]),
    ("4C", ["LO", "XC"]),
]

SECTION_TITLE_MAP = {
    ("2C", "LO"): "2C lo",
    ("2C", "DD"): "2C dd",
    ("2C", "DA"): "2C da",
    ("2C", "DX"): "2C dx",
    ("3C", "LO"): "3C lo",
    ("3C", "XC"): "3C xc",
    ("4C", "LO"): "4C lo",
    ("4C", "XC"): "4C xc",
}


def _fmt_amount(value: Any) -> str:
    return ReportNormalizer.format_decimal(value)


def _bet_type_to_section(bet_type: str, number_key: str) -> tuple[str | None, str]:
    raw = str(bet_type or "").upper().strip()

    if raw == "DD":
        return "2C", "DD"
    if raw == "DA":
        return "2C", "DA"
    if raw == "DX":
        return "2C", "DX"

    token = str(number_key or "").strip().split()[0] if str(number_key or "").strip() else ""
    if token.isdigit():
        if len(token) == 2:
            return "2C", raw
        if len(token) == 3:
            return "3C", raw
        if len(token) == 4:
            return "4C", raw

    return None, raw


def _group_region_items(region_data: dict[str, Any]) -> dict[tuple[str, str], list[dict[str, str]]]:
    grouped: dict[tuple[str, str], list[dict[str, str]]] = {}
    bet_types = region_data.get("bet_types", {}) or {}

    for bet_type, payload in bet_types.items():
        telegram_items = payload.get("telegram_items", []) or []

        for item in telegram_items:
            region_key = str(item.get("region_key", "")).strip().lower()
            number_key = str(item.get("number_key", "")).strip()
            amount = _fmt_amount(item.get("amount", 0))

            section, normalized_bet_type = _bet_type_to_section(bet_type, number_key)
            if not section:
                continue

            key = (section, normalized_bet_type)
            grouped.setdefault(key, []).append(
                {
                    "region": region_key,
                    "number": number_key,
                    "mode": normalized_bet_type,
                    "total": amount,
                }
            )

    for _, rows in grouped.items():
        rows.sort(key=lambda x: (x["region"], x["number"], x["mode"]))

    return grouped


def _build_table(rows: list[dict[str, str]], lang: str = "en") -> list[str]:
    region_w = max(len(t("COL_REGION", lang)), max((len(r["region"]) for r in rows), default=6))
    number_w = max(len(t("COL_NUMBER", lang)), max((len(r["number"]) for r in rows), default=6))
    mode_w = max(len(t("COL_MODE", lang)), max((len(r["mode"]) for r in rows), default=4))
    total_w = max(len(t("COL_TOTAL", lang)), max((len(r["total"]) for r in rows), default=5))

    lines = [
        f"{t('COL_REGION', lang).ljust(region_w)}  {t('COL_NUMBER', lang).ljust(number_w)}  {t('COL_MODE', lang).ljust(mode_w)}  {t('COL_TOTAL', lang).rjust(total_w)}"
    ]

    for row in rows:
        lines.append(
            f"{row['region'].ljust(region_w)}  "
            f"{row['number'].ljust(number_w)}  "
            f"{row['mode'].ljust(mode_w)}  "
            f"{row['total'].rjust(total_w)}"
        )

    return lines


def _generated_at_utc8() -> str:
    tz = timezone(timedelta(hours=8))
    return datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")


def format_report(data: dict, lang: str = "en") -> str:
    target_date = str(data.get("date", "")).strip()
    regions = data.get("regions", {}) or {}
    generated_at = _generated_at_utc8()

    lines: list[str] = []
    lines.append(t("REPORT_NUMBER_DETAIL_TITLE", lang))
    lines.append(f"📅 : {target_date}")
    lines.append("")

    total_rows = 0
    for region_group in REPORT_REGION_GROUPS:
        region_data = regions.get(region_group, {}) or {}
        grouped = _group_region_items(region_data)
        for section_name, mode_list in SECTION_ORDER:
            for mode in mode_list:
                rows = grouped.get((section_name, mode), [])
                total_rows += len(rows)

    max_rows_for_detail = 150

    if total_rows > max_rows_for_detail:
        lines.append(t("REPORT_TOO_MANY_RECORDS", lang, tickets=0, lines=total_rows))
        lines.append(t("REPORT_USE_EXPORT", lang))
        lines.append("")

        for region_group in REPORT_REGION_GROUPS:
            region_data = regions.get(region_group, {}) or {}
            grouped = _group_region_items(region_data)

            region_rows = 0
            for section_name, mode_list in SECTION_ORDER:
                for mode in mode_list:
                    rows = grouped.get((section_name, mode), [])
                    region_rows += len(rows)

            if region_rows > 0:
                lines.append(
                    t(
                        "REPORT_NUMBER_ENTRY_SUMMARY",
                        lang,
                        region=region_group,
                        count=region_rows,
                    )
                )

        lines.append("")
        lines.append("━━━━━━━━━━━━━━━━━━━━")
        lines.append(t("REPORT_GENERATED_AT", lang, ts=generated_at))

        report_text = "\n".join(lines)

        max_telegram_length = 3800
        if len(report_text) > max_telegram_length:
            report_text = report_text[:max_telegram_length] + "\n..."
            report_text += "\n" + t("REPORT_TRUNCATED", lang)

        return report_text

    first_region = True

    for region_group in REPORT_REGION_GROUPS:
        region_data = regions.get(region_group, {}) or {}
        grouped = _group_region_items(region_data)

        if not first_region:
            lines.append("")
            lines.append("━━━━━━━━━━━━━━━━━━━━")
            lines.append("")
        first_region = False

        lines.append(region_group)

        has_any_data = False

        for section_name, mode_list in SECTION_ORDER:
            section_printed = False

            for mode in mode_list:
                rows = grouped.get((section_name, mode), [])

                if not rows:
                    continue

                if not section_printed:
                    lines.append(section_name.lower())
                    section_printed = True

                lines.append(SECTION_TITLE_MAP[(section_name, mode)])
                lines.extend(_build_table(rows, lang))
                lines.append("")
                has_any_data = True

        if not has_any_data:
            lines.append(t("REPORT_REGION_NO_DATA", lang))

    while lines and lines[-1] == "":
        lines.pop()

    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━━━")
    lines.append(t("REPORT_GENERATED_AT", lang, ts=generated_at))

    report_text = "\n".join(lines)

    max_telegram_length = 3800
    if len(report_text) > max_telegram_length:
        report_text = report_text[:max_telegram_length] + "\n..."
        report_text += "\n" + t("REPORT_TRUNCATED", lang)

    return report_text
