from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone

from src.i18n.translator import t
from src.modules.report.constants.report_constants import REPORT_REGION_GROUPS


REGION_WIDTH = 6
NUMBER_WIDTH = 9
MODE_WIDTH = 5
TOTAL_WIDTH = 5


def _generated_at_utc8() -> str:
    tz = timezone(timedelta(hours=8))
    return datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")


def _format_mode(mode_raw: str) -> str:
    mode_key = (mode_raw or "").strip().lower()

    dd_match = re.fullmatch(r"dd(\d+)", mode_key)
    if dd_match:
        amount = dd_match.group(1)
        if amount.isdigit():
            n_value = int(amount) // 10
            if n_value > 0:
                return f"DD{n_value}N"

    mode_map = {
        "lo": "LO1N",
        "da": "DA1N",
        "dx": "DX1N",
        "xc": "XC1N",
    }

    return mode_map.get(mode_key, mode_key.upper())


def _format_row(region: str, number: str, mode: str, total: str) -> str:
    return (
        f"{region:<{REGION_WIDTH}} | "
        f"{number:<{NUMBER_WIDTH}} | "
        f"{mode:<{MODE_WIDTH}} | "
        f"{total:>{TOTAL_WIDTH}}"
    )


def _header_row(lang: str = "en") -> str:
    return _format_row(
        t("COL_REGION", lang),
        t("COL_NUMBER", lang),
        t("COL_MODE", lang),
        t("COL_TOTAL", lang),
    )


def _format_ticket_line(raw_line: object, lang: str = "en") -> str:
    text = str(raw_line or "").strip()
    if not text:
        return t("REPORT_TICKET_NO_DETAIL", lang)

    if "|" in text:
        parts = [part.strip() for part in text.split("|")]
        if len(parts) >= 4:
            region = parts[0].upper()
            number = parts[1]
            mode = parts[2].upper()
            total = parts[3]
            return _format_row(region, number, mode, total)

    tokens = text.split()
    if len(tokens) < 3:
        return text.upper()

    region = tokens[0].upper()
    number_tokens = tokens[1:-1]
    tail = tokens[-1]

    mode = ""
    total = ""

    match = re.fullmatch(r"([A-Za-z]+)(\d+)", tail)
    if match:
        mode = _format_mode(tail)
        total = match.group(2)
    elif len(tokens) >= 4 and tokens[-2].isalpha():
        number_tokens = tokens[1:-2]
        mode = _format_mode(tokens[-2])
        total = tokens[-1]
    else:
        mode = tail.upper()

    number = " ".join(number_tokens)
    return _format_row(region, number, mode, total)


def format_report(data: dict, lang: str = "en") -> str:
    target_date = str(data.get("date", "")).strip()
    regions = data.get("regions", {}) or {}
    generated_at = _generated_at_utc8()

    lines: list[str] = []

    lines.append("```")
    lines.append(t("REPORT_TRANSACTION_TITLE", lang))
    lines.append("")
    lines.append(f"📅 : {target_date}")
    lines.append("")

    total_tickets = 0
    total_lines = 0
    for region_group in REPORT_REGION_GROUPS:
        region_data = regions.get(region_group, {}) or {}
        tickets = region_data.get("tickets", []) or []
        total_tickets += len(tickets)
        for ticket in tickets:
            ticket_lines = ticket.get("lines", []) or []
            total_lines += len(ticket_lines)

    max_lines_for_detail = 100
    max_tickets_for_detail = 20

    if total_lines > max_lines_for_detail or total_tickets > max_tickets_for_detail:
        lines.append(t("REPORT_TOO_MANY_RECORDS", lang, tickets=total_tickets, lines=total_lines))
        lines.append(t("REPORT_USE_EXPORT", lang))
        lines.append("")

        for region_group in REPORT_REGION_GROUPS:
            region_data = regions.get(region_group, {}) or {}
            tickets = region_data.get("tickets", []) or []

            if not tickets:
                continue

            region_lines = 0
            region_total = 0.0
            for ticket in tickets:
                ticket_lines = ticket.get("lines", []) or []
                region_lines += len(ticket_lines)
                try:
                    region_total += float(str(ticket.get("total_amount", "0")).strip())
                except Exception:
                    pass

            lines.append(
                t(
                    "REPORT_REGION_SUMMARY",
                    lang,
                    region=region_group,
                    tickets=len(tickets),
                    lines=region_lines,
                    total=f"{region_total:,.0f}",
                )
            )

        lines.append("")
        lines.append("━━━━━━━━━━━━━━━━━━━━")
        lines.append(t("REPORT_GENERATED_AT", lang, ts=generated_at))
        lines.append("```")

        report_text = "\n".join(lines)

        max_telegram_length = 3800
        if len(report_text) > max_telegram_length:
            report_text = report_text[:max_telegram_length] + "\n..." + "\n```"
            report_text += "\n" + t("REPORT_TRUNCATED", lang)

        return report_text

    for region_group in REPORT_REGION_GROUPS:
        region_data = regions.get(region_group, {}) or {}
        tickets = region_data.get("tickets", []) or []

        lines.append("━━━━━━━━━━━━━━━━━━━━")
        lines.append(f"📍 {region_group}")
        lines.append("━━━━━━━━━━━━━━━━━━━━")
        lines.append("")

        if not tickets:
            lines.append(t("REPORT_REGION_NO_DATA", lang))
            lines.append("")
            continue

        for index, ticket in enumerate(tickets):
            ticket_no = str(ticket.get("ticket_no", "")).strip().upper() or "Ticket"
            ticket_lines = ticket.get("lines", []) or []
            ticket_total = str(ticket.get("total_amount", "")).strip()

            lines.append(f"🎫 : {ticket_no}")
            lines.append("--------------------------------")
            lines.append(_header_row(lang))

            if ticket_lines:
                for raw_line in ticket_lines:
                    lines.append(_format_ticket_line(raw_line, lang))
            else:
                lines.append(t("REPORT_TICKET_NO_DETAIL", lang))

            lines.append("")
            lines.append(t("REPORT_TICKET_TOTAL", lang, value=ticket_total))
            lines.append("")

            if index != len(tickets) - 1:
                lines.append("")

    lines.append("━━━━━━━━━━━━━━━━━━━━")
    lines.append(t("REPORT_GENERATED_AT", lang, ts=generated_at))
    lines.append("```")

    report_text = "\n".join(lines)

    max_telegram_length = 3800
    if len(report_text) > max_telegram_length:
        report_text = report_text[:max_telegram_length] + "\n..." + "\n```"
        report_text += "\n" + t("REPORT_TRUNCATED", lang)

    return report_text
