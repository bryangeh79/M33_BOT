from __future__ import annotations

from datetime import datetime, timezone, timedelta
from html import escape
import re
from typing import Any

from src.i18n.translator import t
from src.modules.report.constants.report_constants import REPORT_REGION_GROUPS


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


def _generated_at_utc8() -> str:
    tz = timezone(timedelta(hours=8))
    return datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")


def _html_document(title: str, body: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{escape(title)}</title>
    <style>
        * {{
            box-sizing: border-box;
        }}

        body {{
            margin: 0;
            padding: 20px;
            background: #f5f7fb;
            color: #111827;
            font-family: Arial, Helvetica, sans-serif;
        }}

        .report {{
            max-width: 1040px;
            margin: 0 auto;
        }}

        .header-card,
        .region-card,
        .footer-card {{
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 14px;
        }}

        .header-card {{
            padding: 20px 22px;
            margin-bottom: 18px;
        }}

        .title {{
            margin: 0 0 8px;
            font-size: 28px;
            line-height: 1.2;
            font-weight: 700;
            color: #111827;
        }}

        .meta {{
            margin: 0;
            font-size: 14px;
            line-height: 1.6;
            color: #4b5563;
        }}

        .region-card {{
            padding: 18px;
            margin-bottom: 18px;
        }}

        .region-title {{
            margin: 0 0 14px;
            font-size: 20px;
            line-height: 1.25;
            font-weight: 700;
            color: #111827;
        }}

        .ticket-card {{
            background: #fafafa;
            border: 1px solid #eceff3;
            border-radius: 12px;
            padding: 14px;
            margin-bottom: 14px;
        }}

        .ticket-card:last-child {{
            margin-bottom: 0;
        }}

        .ticket-title {{
            margin: 0 0 10px;
            font-size: 15px;
            line-height: 1.3;
            font-weight: 700;
            color: #111827;
        }}

        .table-wrap {{
            width: 100%;
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
            border-radius: 10px;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            table-layout: fixed;
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 10px;
            overflow: hidden;
        }}

        .standard-table {{
            min-width: 560px;
        }}

        .compact-table {{
            min-width: 100%;
        }}

        th,
        td {{
            padding: 10px 12px;
            border-bottom: 1px solid #e5e7eb;
            font-size: 14px;
            line-height: 1.4;
            vertical-align: top;
        }}

        th {{
            background: #f9fafb;
            text-align: left;
            font-weight: 700;
            color: #374151;
        }}

        tbody tr:last-child td {{
            border-bottom: none;
        }}

        .col-region {{
            width: 96px;
            white-space: nowrap;
        }}

        .col-number {{
            width: auto;
            white-space: nowrap;
        }}

        .col-mode {{
            width: 96px;
            white-space: nowrap;
        }}

        .col-total {{
            width: 96px;
            text-align: right;
            white-space: nowrap;
        }}

        .compact-table .col-region {{
            width: 72px;
        }}

        .compact-table .col-number {{
            width: 84px;
        }}

        .compact-table .col-mode {{
            width: 64px;
        }}

        .compact-table .col-total {{
            width: 84px;
        }}

        .ticket-total {{
            margin-top: 10px;
            text-align: right;
            font-size: 14px;
            line-height: 1.4;
            font-weight: 700;
            color: #111827;
        }}

        .no-data {{
            font-size: 14px;
            line-height: 1.4;
            color: #6b7280;
        }}

        .section-label {{
            margin: 12px 0 8px;
            font-size: 16px;
            line-height: 1.3;
            font-weight: 700;
            color: #111827;
            text-transform: uppercase;
        }}

        .sub-label {{
            margin: 0 0 8px;
            font-size: 14px;
            line-height: 1.4;
            font-weight: 700;
            color: #4b5563;
        }}

        .footer-card {{
            padding: 14px 18px;
            margin-top: 18px;
        }}

        .footer-meta {{
            margin: 0;
            font-size: 13px;
            line-height: 1.5;
            color: #4b5563;
        }}

        @media (max-width: 768px) {{
            body {{
                padding: 12px;
            }}

            .report {{
                max-width: 100%;
            }}

            .header-card {{
                padding: 16px;
                margin-bottom: 14px;
            }}

            .region-card {{
                padding: 14px;
                margin-bottom: 14px;
            }}

            .ticket-card {{
                padding: 12px;
                margin-bottom: 12px;
            }}

            .title {{
                font-size: 24px;
            }}

            .region-title {{
                font-size: 18px;
                margin-bottom: 12px;
            }}

            th,
            td {{
                padding: 9px 10px;
                font-size: 13px;
            }}

            .ticket-title,
            .ticket-total,
            .no-data,
            .meta,
            .sub-label {{
                font-size: 13px;
            }}

            .section-label {{
                font-size: 15px;
            }}

            .standard-table {{
                min-width: 520px;
            }}

            .compact-table {{
                min-width: 100%;
            }}

            .compact-table .col-region {{
                width: 56px;
            }}

            .compact-table .col-number {{
                width: 72px;
            }}

            .compact-table .col-mode {{
                width: 52px;
            }}

            .compact-table .col-total {{
                width: 72px;
            }}

            .compact-table th,
            .compact-table td {{
                padding: 8px 6px;
                font-size: 12px;
            }}
        }}

        @media (max-width: 420px) {{
            body {{
                padding: 10px;
            }}

            .header-card,
            .region-card,
            .footer-card {{
                border-radius: 12px;
            }}

            .header-card {{
                padding: 14px;
            }}

            .region-card {{
                padding: 12px;
            }}

            .title {{
                font-size: 22px;
            }}

            .region-title {{
                font-size: 17px;
            }}

            .compact-table th,
            .compact-table td {{
                padding: 7px 5px;
                font-size: 11px;
            }}

            .compact-table .col-region {{
                width: 50px;
            }}

            .compact-table .col-number {{
                width: 64px;
            }}

            .compact-table .col-mode {{
                width: 46px;
            }}

            .compact-table .col-total {{
                width: 64px;
            }}
        }}
    </style>
</head>
<body>
    <div class="report">
        {body}
    </div>
</body>
</html>"""


def _normalize_mode(mode: str) -> str:
    value = str(mode or "").strip().upper()
    if not value:
        return value

    match = re.fullmatch(r"([A-Z]+)(\d+)", value)
    if not match:
        return value

    mode_code, amount = match.groups()
    if amount == "10":
        return f"{mode_code}1N"
    return value


def _parse_transaction_line(item) -> dict[str, str]:
    if isinstance(item, dict):
        region = str(item.get("region", "")).strip().upper()
        number = str(item.get("number", "")).strip()
        mode = _normalize_mode(str(item.get("mode", "")).strip())
        total = str(item.get("total", "")).strip()

        if region or number or mode or total:
            return {
                "region": region,
                "number": number,
                "mode": mode,
                "total": total,
            }

        raw = str(item.get("raw", "")).strip()
    else:
        raw = str(item).strip()

    if not raw:
        return {"region": "", "number": "", "mode": "", "total": ""}

    parts = raw.split()
    if len(parts) < 2:
        return {"region": raw.upper(), "number": "", "mode": "", "total": ""}

    region = parts[0].upper()
    total = parts[-1]
    middle = parts[1:-1]

    mode = ""
    number = ""

    if middle:
        raw_mode = middle[-1]
        number_parts = middle[:-1]
        mode = _normalize_mode(raw_mode)
        number = " ".join(number_parts).strip()

    return {
        "region": region,
        "number": number,
        "mode": mode,
        "total": total,
    }


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


def _group_number_detail_region_items(region_data: dict[str, Any]) -> dict[tuple[str, str], list[dict[str, str]]]:
    grouped: dict[tuple[str, str], list[dict[str, str]]] = {}
    bet_types = region_data.get("bet_types", {}) or {}

    for bet_type, payload in bet_types.items():
        html_items = payload.get("html_items", []) or payload.get("telegram_items", []) or []

        for item in html_items:
            region_key = str(item.get("region_key", "")).strip().lower()
            number_key = str(item.get("number_key", "")).strip()
            amount = str(item.get("amount", "")).strip()

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


def build_transaction_report_html(data: dict, lang: str = "en") -> str:
    target_date = str(data.get("date", "")).strip()
    regions = data.get("regions", {}) or {}
    generated_at = _generated_at_utc8()

    parts: list[str] = []
    parts.append('<div class="header-card">')
    parts.append(f'<h1 class="title">{escape(t("REPORT_TRANSACTION_TITLE", lang=lang))}</h1>')
    parts.append(f'<p class="meta">{escape(t("REPORT_DATE_LABEL", lang=lang, date=target_date))}</p>')
    parts.append(f'<p class="meta">{escape(t("REPORT_GENERATED_AT", lang=lang, ts=generated_at))}</p>')
    parts.append('</div>')

    for region_group in REPORT_REGION_GROUPS:
        region_data = regions.get(region_group, {}) or {}
        tickets = region_data.get("tickets", []) or []

        parts.append('<section class="region-card">')
        parts.append(f'<h2 class="region-title">{escape(region_group)}</h2>')

        if not tickets:
            parts.append(f'<div class="no-data">{escape(t("REPORT_REGION_NO_DATA", lang=lang))}</div>')
            parts.append('</section>')
            continue

        for ticket in tickets:
            ticket_no = str(ticket.get("ticket_no", "")).strip().upper() or "Ticket"
            ticket_lines = ticket.get("lines", []) or []
            ticket_total = str(ticket.get("total_amount", "")).strip()

            parts.append('<div class="ticket-card">')
            parts.append(f'<div class="ticket-title">{escape(ticket_no)}</div>')
            parts.append('<div class="table-wrap">')
            parts.append(
                f"""
                <table class="standard-table">
                    <thead>
                        <tr>
                            <th class="col-region">{escape(t('COL_REGION', lang=lang))}</th>
                            <th class="col-number">{escape(t('COL_NUMBER', lang=lang))}</th>
                            <th class="col-mode">{escape(t('COL_MODE', lang=lang))}</th>
                            <th class="col-total">{escape(t('COL_TOTAL', lang=lang))}</th>
                        </tr>
                    </thead>
                    <tbody>
                """
            )

            if ticket_lines:
                for item in ticket_lines:
                    line = _parse_transaction_line(item)
                    parts.append(
                        f"""
                        <tr>
                            <td class="col-region">{escape(line["region"])}</td>
                            <td class="col-number">{escape(line["number"])}</td>
                            <td class="col-mode">{escape(line["mode"])}</td>
                            <td class="col-total">{escape(line["total"])}</td>
                        </tr>
                        """
                    )
            else:
                parts.append(f'<tr><td colspan="4" class="no-data">{escape(t("REPORT_TICKET_NO_DETAIL", lang=lang))}</td></tr>')

            parts.append("</tbody></table>")
            parts.append("</div>")
            parts.append(f'<div class="ticket-total">{escape(t("REPORT_TICKET_TOTAL", lang=lang, value=ticket_total))}</div>')
            parts.append("</div>")

        parts.append("</section>")

    parts.append('<div class="footer-card">')
    parts.append(f'<p class="footer-meta">{escape(t("REPORT_GENERATED_AT", lang=lang, ts=generated_at))}</p>')
    parts.append('</div>')

    return _html_document(t("REPORT_TRANSACTION_TITLE", lang=lang), "".join(parts))


def build_number_detail_report_html(data: dict, lang: str = "en") -> str:
    target_date = str(data.get("date", "")).strip()
    regions = data.get("regions", {}) or {}
    generated_at = _generated_at_utc8()

    parts: list[str] = []
    parts.append('<div class="header-card">')
    parts.append(f'<h1 class="title">{escape(t("REPORT_NUMBER_DETAIL_TITLE", lang=lang))}</h1>')
    parts.append(f'<p class="meta">{escape(t("REPORT_DATE_LABEL", lang=lang, date=target_date))}</p>')
    parts.append(f'<p class="meta">{escape(t("REPORT_GENERATED_AT", lang=lang, ts=generated_at))}</p>')
    parts.append('</div>')

    for region_group in REPORT_REGION_GROUPS:
        region_data = regions.get(region_group, {}) or {}
        grouped = _group_number_detail_region_items(region_data)

        parts.append('<section class="region-card">')
        parts.append(f'<h2 class="region-title">{escape(region_group)}</h2>')

        has_any_data = False

        for section_name, mode_list in SECTION_ORDER:
            section_printed = False

            for mode in mode_list:
                rows = grouped.get((section_name, mode), [])
                if not rows:
                    continue

                if not section_printed:
                    parts.append(f'<div class="section-label">{escape(section_name)}</div>')
                    section_printed = True

                parts.append(f'<div class="sub-label">{escape(SECTION_TITLE_MAP[(section_name, mode)])}</div>')
                parts.append('<div class="table-wrap">')
                parts.append(
                    f"""
                    <table class="compact-table">
                        <thead>
                            <tr>
                                <th class="col-region">{escape(t('COL_REGION', lang=lang))}</th>
                                <th class="col-number">{escape(t('COL_NUMBER', lang=lang))}</th>
                                <th class="col-mode">{escape(t('COL_MODE', lang=lang))}</th>
                                <th class="col-total">{escape(t('COL_TOTAL', lang=lang))}</th>
                            </tr>
                        </thead>
                        <tbody>
                    """
                )

                for row in rows:
                    parts.append(
                        f"""
                        <tr>
                            <td class="col-region">{escape(row["region"])}</td>
                            <td class="col-number">{escape(row["number"])}</td>
                            <td class="col-mode">{escape(row["mode"])}</td>
                            <td class="col-total">{escape(row["total"])}</td>
                        </tr>
                        """
                    )

                parts.append("</tbody></table>")
                parts.append("</div>")
                has_any_data = True

        if not has_any_data:
            parts.append(f'<div class="no-data">{escape(t("REPORT_REGION_NO_DATA", lang=lang))}</div>')

        parts.append('</section>')

    parts.append('<div class="footer-card">')
    parts.append(f'<p class="footer-meta">{escape(t("REPORT_GENERATED_AT", lang=lang, ts=generated_at))}</p>')
    parts.append('</div>')

    return _html_document(t("REPORT_NUMBER_DETAIL_TITLE", lang=lang), "".join(parts))
