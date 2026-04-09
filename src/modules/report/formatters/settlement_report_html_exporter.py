from __future__ import annotations

from datetime import datetime, timedelta, timezone
from html import escape
from typing import Any

from src.i18n.translator import t


def _fmt_money(value: Any) -> str:
    try:
        value = float(value)
    except Exception:
        value = 0.0

    if value.is_integer():
        return str(int(value))
    return f"{value:.2f}".rstrip("0").rstrip(".")


def _generated_at_utc8() -> str:
    tz = timezone(timedelta(hours=8))
    return datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")


def _winner_mode(item: dict[str, Any]) -> str:
    bet_type = escape(str(item.get("bet_type", "")).strip().upper())
    bet_code = escape(str(item.get("bet_code", "")).strip().upper())

    if bet_type and bet_code:
        return f"{bet_type} {bet_code}"
    if bet_type:
        return bet_type
    if bet_code:
        return bet_code
    return "-"


def export_settlement_report_html(report: dict[str, Any], lang: str = "en") -> str:
    date_text = escape(str(report.get("date", "")).strip())
    generated_at = escape(_generated_at_utc8())

    regions = report.get("regions", {}) or {}
    summary = report.get("summary", {}) or {}
    winner_details = report.get("winner_details", []) or []

    region_blocks: list[str] = []

    for region_group in ("MN", "MT", "MB"):
        region_data = regions.get(region_group, {}) or {}
        bet_total = _fmt_money(region_data.get("bet_total", 0))
        payout_total = _fmt_money(region_data.get("payout_total", 0))
        agent_comm = _fmt_money(region_data.get("commission", 0))
        region_total = _fmt_money(region_data.get("settlement", 0))

        region_blocks.append(
            f"""
            <section class="region-card">
                <h2>{escape(region_group)}</h2>
                <div class="kv-grid">
                    <div class="kv-row"><span class="label">{escape(t('REPORT_BET_TOTAL', lang=lang))}</span><span class="value">{escape(bet_total)}</span></div>
                    <div class="kv-row"><span class="label">{escape(t('REPORT_PAYOUT', lang=lang))}</span><span class="value">{escape(payout_total)}</span></div>
                    <div class="kv-row"><span class="label">{escape(t('REPORT_AGENT_COMM', lang=lang))}</span><span class="value">{escape(agent_comm)}</span></div>
                    <div class="kv-row total-row"><span class="label">{escape(t('REPORT_REGION_SETTLEMENT', lang=lang, region=region_group))}</span><span class="value">{escape(region_total)}</span></div>
                </div>
            </section>
            """
        )

    total_settlement = _fmt_money(summary.get("total_settlement", 0))

    winner_sections: list[str] = []
    if not winner_details:
        winner_sections.append(f'<div class="no-data">{escape(t("REPORT_NO_WINNING", lang=lang))}</div>')
    else:
        current_ticket = None
        current_rows: list[str] = []
        current_ticket_total = 0.0

        def flush_ticket(ticket_no: str | None, rows_html: list[str], ticket_total: float) -> None:
            if not ticket_no:
                return
            winner_sections.append(
                f"""
                <section class="ticket-card">
                    <h3>{escape(ticket_no)}</h3>
                    <table>
                        <thead>
                            <tr>
                                <th>{escape(t('COL_REGION', lang=lang))}</th>
                                <th>{escape(t('COL_NUMBER', lang=lang))}</th>
                                <th>{escape(t('COL_MODE', lang=lang))}</th>
                                <th class="num">{escape(t('COL_BET', lang=lang))}</th>
                                <th class="num">{escape(t('COL_WIN', lang=lang))}</th>
                            </tr>
                        </thead>
                        <tbody>
                            {''.join(rows_html)}
                        </tbody>
                    </table>
                    <div class="ticket-win">{escape(t('REPORT_TICKET_WIN', lang=lang, value=_fmt_money(ticket_total)))}</div>
                </section>
                """
            )

        for item in winner_details:
            ticket_no = str(item.get("ticket_no", "")).strip().upper() or "-"
            region = escape(str(item.get("region", "")).strip().upper() or "-")
            numbers = item.get("numbers", []) or []
            number_text = escape(" ".join(str(x) for x in numbers) if numbers else "-")
            mode_text = _winner_mode(item)
            bet_text = escape(_fmt_money(item.get("bet_total", 0)))
            win_text = escape(_fmt_money(item.get("payout", 0)))

            try:
                payout_value = float(item.get("payout", 0) or 0)
            except Exception:
                payout_value = 0.0

            if current_ticket is None:
                current_ticket = ticket_no

            if ticket_no != current_ticket:
                flush_ticket(current_ticket, current_rows, current_ticket_total)
                current_ticket = ticket_no
                current_rows = []
                current_ticket_total = 0.0

            current_rows.append(
                f"""
                <tr>
                    <td>{region}</td>
                    <td>{number_text}</td>
                    <td>{mode_text}</td>
                    <td class="num">{bet_text}</td>
                    <td class="num">{win_text}</td>
                </tr>
                """
            )
            current_ticket_total += payout_value

        flush_ticket(current_ticket, current_rows, current_ticket_total)

    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{escape(t('REPORT_SETTLEMENT_TITLE', lang=lang))} - {date_text}</title>
    <style>
        body {{
            font-family: Arial, Helvetica, sans-serif;
            margin: 24px;
            color: #222;
            background: #fff;
        }}
        h1 {{
            margin: 0 0 6px 0;
        }}
        .meta {{
            margin-bottom: 18px;
            color: #555;
            font-size: 14px;
        }}
        .region-card, .summary-card, .ticket-card {{
            border: 1px solid #ddd;
            border-radius: 10px;
            padding: 16px;
            margin-bottom: 16px;
            background: #fff;
        }}
        .kv-grid {{
            display: grid;
            gap: 10px;
        }}
        .kv-row {{
            display: flex;
            justify-content: space-between;
            gap: 16px;
            border-bottom: 1px dashed #ddd;
            padding-bottom: 6px;
        }}
        .kv-row.total-row {{
            border-bottom: none;
            font-weight: 700;
            padding-top: 4px;
        }}
        .label {{
            color: #444;
        }}
        .value {{
            font-weight: 600;
        }}
        .summary-card {{
            background: #fafafa;
        }}
        .summary-title, .winner-title {{
            font-size: 20px;
            font-weight: 700;
            margin: 0 0 12px 0;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 8px;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px 10px;
            text-align: left;
            vertical-align: top;
        }}
        th {{
            background: #f5f5f5;
        }}
        .num {{
            text-align: right;
        }}
        .ticket-win {{
            margin-top: 10px;
            font-weight: 700;
        }}
        .no-data {{
            color: #666;
            font-style: italic;
        }}
        .footer {{
            margin-top: 22px;
            padding-top: 12px;
            border-top: 1px solid #ddd;
            color: #666;
            font-size: 13px;
        }}
    </style>
</head>
<body>
    <h1>{escape(t('REPORT_SETTLEMENT_TITLE', lang=lang))}</h1>
    <div class="meta">{escape(t('REPORT_DATE_LABEL', lang=lang, date=date_text))}</div>

    {''.join(region_blocks)}

    <section class="summary-card">
        <div class="summary-title">{escape(t('REPORT_TOTAL_SETTLEMENT', lang=lang))}</div>
        <div class="value">{escape(total_settlement)}</div>
    </section>

    <section class="summary-card">
        <div class="winner-title">{escape(t('REPORT_WINNING_DETAILS', lang=lang))}</div>
        {''.join(winner_sections)}
    </section>

    <div class="footer">{escape(t('REPORT_GENERATED_AT', lang=lang, ts=generated_at))}</div>
</body>
</html>
"""
    return html
