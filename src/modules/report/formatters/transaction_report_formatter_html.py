from __future__ import annotations

import re
from datetime import datetime, timezone, timedelta

from src.modules.report.constants.report_constants import REPORT_REGION_GROUPS


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


def format_report_html(data: dict) -> str:
    target_date = str(data.get("date", "")).strip()
    regions = data.get("regions", {}) or {}
    generated_at = _generated_at_utc8()

    html: list[str] = []

    html.append("""
    <html>
    <head>
        <style>
            body {
                font-family: monospace;
                background: #ffffff;
                color: #000000;
                padding: 16px;
            }
            .title {
                font-size: 18px;
                font-weight: bold;
                margin-bottom: 8px;
            }
            .section {
                margin-top: 20px;
            }
            .region-title {
                font-weight: bold;
                border-bottom: 2px solid #000;
                padding-bottom: 4px;
                margin-bottom: 10px;
            }
            .ticket {
                margin-bottom: 16px;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 6px;
            }
            th, td {
                text-align: left;
                padding: 4px 6px;
            }
            th {
                border-bottom: 1px solid #000;
            }
            .right {
                text-align: right;
            }
            .ticket-total {
                margin-top: 6px;
                font-weight: bold;
            }
            .no-data {
                color: #666;
            }
            .footer {
                margin-top: 30px;
                border-top: 1px solid #000;
                padding-top: 10px;
                font-size: 12px;
            }
        </style>
    </head>
    <body>
    """)

    html.append(f"<div class='title'>📊 Transaction Report</div>")
    html.append(f"<div>📅 : {target_date}</div>")

    for region_group in REPORT_REGION_GROUPS:
        region_data = regions.get(region_group, {}) or {}
        tickets = region_data.get("tickets", []) or []

        html.append(f"<div class='section'>")
        html.append(f"<div class='region-title'>📍 {region_group}</div>")

        if not tickets:
            html.append("<div class='no-data'>No data</div>")
            html.append("</div>")
            continue

        for ticket in tickets:
            ticket_no = str(ticket.get("ticket_no", "")).strip().upper() or "Ticket"
            ticket_lines = ticket.get("lines", []) or []
            ticket_total = str(ticket.get("total_amount", ""))

            html.append("<div class='ticket'>")
            html.append(f"<div>🎫 : {ticket_no}</div>")

            html.append("""
            <table>
                <thead>
                    <tr>
                        <th>Region</th>
                        <th>Number</th>
                        <th>Mode</th>
                        <th class="right">Total</th>
                    </tr>
                </thead>
                <tbody>
            """)

            if ticket_lines:
                for raw_line in ticket_lines:
                    parts = str(raw_line).split()

                    region = parts[0].upper() if len(parts) > 0 else ""
                    number = parts[1] if len(parts) > 1 else ""
                    mode = _format_mode(parts[2]) if len(parts) > 2 else ""
                    total = parts[-1] if len(parts) > 0 else ""

                    html.append(f"""
                    <tr>
                        <td>{region}</td>
                        <td>{number}</td>
                        <td>{mode}</td>
                        <td class="right">{total}</td>
                    </tr>
                    """)

            else:
                html.append("""
                <tr>
                    <td colspan="4" class="no-data">No detail</td>
                </tr>
                """)

            html.append("</tbody></table>")
            html.append(f"<div class='ticket-total'>Ticket Total: {ticket_total}</div>")
            html.append("</div>")

        html.append("</div>")

    html.append(f"""
    <div class='footer'>
        🕒 Generated at: {generated_at} (UTC+8)
    </div>
    """)

    html.append("</body></html>")

    return "".join(html)
