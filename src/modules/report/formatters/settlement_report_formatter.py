from __future__ import annotations

from datetime import datetime, timezone, timedelta
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
    bet_type = str(item.get("bet_type", "")).strip().upper()
    bet_code = str(item.get("bet_code", "")).strip().upper()

    if bet_type and bet_code:
        return f"{bet_type} {bet_code}"
    if bet_type:
        return bet_type
    if bet_code:
        return bet_code
    return "-"


def _kv_line(label: str, value: str, width: int = 18) -> str:
    return f"{label.ljust(width)}: {value}"


def format_settlement_report_telegram(report: dict[str, Any], lang: str = "en") -> str:
    date_text = str(report.get("date", "")).strip()

    regions = report.get("regions", {}) or {}
    summary = report.get("summary", {}) or {}
    winner_details = report.get("winner_details", []) or []

    lines: list[str] = []
    lines.append(t("REPORT_SETTLEMENT_TITLE", lang))
    lines.append(t("REPORT_DATE_LABEL", lang, date=date_text))
    lines.append("")

    total_settlement_calc = 0.0

    for region_group in ("MN", "MT", "MB"):
        region_data = regions.get(region_group, {}) or {}

        bet_total = float(region_data.get("bet_total", 0) or 0)
        payout_total = float(region_data.get("payout_total", 0) or 0)
        commission = float(region_data.get("commission", 0) or 0)

        settlement = float(region_data.get("settlement", bet_total - payout_total - commission) or 0)
        total_settlement_calc += settlement

        lines.append("--------------------")
        lines.append(region_group)
        lines.append("")
        lines.append(_kv_line(t("REPORT_BET_TOTAL", lang), _fmt_money(bet_total)))
        lines.append(_kv_line(t("REPORT_PAYOUT", lang), _fmt_money(payout_total)))
        lines.append(_kv_line(t("REPORT_AGENT_COMM", lang), _fmt_money(commission)))
        lines.append(_kv_line(t("REPORT_REGION_SETTLEMENT", lang, region=region_group), _fmt_money(settlement)))
        lines.append("")
        lines.append("")

    total_settlement = summary.get("total_settlement", total_settlement_calc)
    lines.append(_kv_line(t("REPORT_TOTAL_SETTLEMENT", lang), _fmt_money(total_settlement)))
    lines.append("")
    lines.append("---------------------------------")
    lines.append(t("REPORT_WINNING_DETAILS", lang))
    lines.append("")

    if not winner_details:
        lines.append(t("REPORT_NO_WINNING", lang))
        lines.append("")
        lines.append(t("REPORT_GENERATED_AT", lang, ts=_generated_at_utc8()))
        return "\n".join(lines)

    current_ticket = None
    current_rows: list[dict[str, str]] = []
    current_ticket_total = 0.0

    def flush_ticket(ticket_no: str | None, rows: list[dict[str, str]], ticket_total: float) -> None:
        if not ticket_no:
            return

        region_w = max(len(t("COL_REGION", lang)), max((len(r["region"]) for r in rows), default=6))
        number_w = max(len(t("COL_NUMBER", lang)), max((len(r["number"]) for r in rows), default=6))
        mode_w = max(len(t("COL_MODE", lang)), max((len(r["mode"]) for r in rows), default=4))
        bet_w = max(len(t("COL_BET", lang)), max((len(r["bet"]) for r in rows), default=3))
        win_w = max(len(t("COL_WIN", lang)), max((len(r["win"]) for r in rows), default=3))

        lines.append(ticket_no)
        lines.append(
            f"{t('COL_REGION', lang).ljust(region_w)} | "
            f"{t('COL_NUMBER', lang).ljust(number_w)} | "
            f"{t('COL_MODE', lang).ljust(mode_w)} | "
            f"{t('COL_BET', lang).rjust(bet_w)} | "
            f"{t('COL_WIN', lang).rjust(win_w)}"
        )

        for row in rows:
            lines.append(
                f"{row['region'].ljust(region_w)} | "
                f"{row['number'].ljust(number_w)} | "
                f"{row['mode'].ljust(mode_w)} | "
                f"{row['bet'].rjust(bet_w)} | "
                f"{row['win'].rjust(win_w)}"
            )

        lines.append("")
        lines.append(t("REPORT_TICKET_WIN", lang, value=_fmt_money(ticket_total)))
        lines.append("--------------------")
        lines.append("")

    for item in winner_details:
        ticket_no = str(item.get("ticket_no", "")).strip().upper() or "-"
        region = str(item.get("display_region", "") or item.get("region", "")).strip().upper() or "-"
        number_text = str(item.get("display_number", "")).strip()
        if not number_text:
            numbers = item.get("numbers", []) or []
            number_text = " ".join(str(x) for x in numbers) if numbers else "-"

        mode_text = _winner_mode(item)
        bet_text = _fmt_money(item.get("display_bet", item.get("bet_total", 0)))
        win_text = _fmt_money(item.get("payout", 0))

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
            {
                "region": region,
                "number": number_text or "-",
                "mode": mode_text,
                "bet": bet_text,
                "win": win_text,
            }
        )
        current_ticket_total += payout_value

    flush_ticket(current_ticket, current_rows, current_ticket_total)

    lines.append(t("REPORT_GENERATED_AT", lang, ts=_generated_at_utc8()))
    return "\n".join(lines)
