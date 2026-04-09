from datetime import date
from decimal import Decimal

from src.i18n.translator import t


def _format_decimal(value: Decimal) -> str:
    if value == value.to_integral():
        return str(int(value))
    return format(value.normalize(), "f").rstrip("0").rstrip(".")


def _safe_text(value) -> str:
    return str(value).strip() if value is not None else ""


def _mode_with_amount(result: dict) -> str:
    display_mode = _safe_text(result.get("display_mode", "")).upper() or "-"
    amount_text = _format_decimal(result.get("amount", Decimal("0")))

    if display_mode == "DA":
        return f"DA{amount_text}N"
    if display_mode == "DX":
        return f"DX{amount_text}N"

    return display_mode


def _build_column_widths(calculated_results: list[dict], lang: str = "en") -> dict[str, int]:
    region_values: list[str] = []
    number_values: list[str] = []
    mode_values: list[str] = []
    total_values: list[str] = []

    for result in calculated_results:
        region_label = _safe_text(result.get("region_label", "")).upper() or "-"
        numbers = result.get("numbers", [])
        if isinstance(numbers, list) and numbers:
            numbers_str = " ".join(str(x).strip() for x in numbers if str(x).strip())
        else:
            numbers_str = _safe_text(result.get("numbers_str", "")) or "-"

        display_mode = _mode_with_amount(result)
        total = _format_decimal(result.get("total", Decimal("0")))

        region_values.append(region_label)
        number_values.append(numbers_str)
        mode_values.append(display_mode)
        total_values.append(total)

    return {
        "region": max([len(t("COL_REGION", lang)), 6] + [len(x) for x in region_values]),
        "number": max([len(t("COL_NUMBER", lang)), 8] + [len(x) for x in number_values]),
        "mode": max([len(t("COL_MODE", lang)), 4] + [len(x) for x in mode_values]),
        "total": max([len(t("COL_TOTAL", lang)), 5] + [len(x) for x in total_values]),
    }


def _build_table_header(widths: dict[str, int], lang: str = "en") -> str:
    return (
        f"{t('COL_REGION', lang).ljust(widths['region'])} | "
        f"{t('COL_NUMBER', lang).ljust(widths['number'])} | "
        f"{t('COL_MODE', lang).ljust(widths['mode'])} | "
        f"{t('COL_TOTAL', lang).rjust(widths['total'])}"
    )


def _build_table_row(result: dict, widths: dict[str, int]) -> str:
    region_label = _safe_text(result.get("region_label", "")).upper() or "-"

    numbers = result.get("numbers", [])
    if isinstance(numbers, list) and numbers:
        numbers_str = " ".join(str(x).strip() for x in numbers if str(x).strip())
    else:
        numbers_str = _safe_text(result.get("numbers_str", "")) or "-"

    display_mode = _mode_with_amount(result)
    total = _format_decimal(result.get("total", Decimal("0")))

    return (
        f"{region_label.ljust(widths['region'])} | "
        f"{numbers_str.ljust(widths['number'])} | "
        f"{display_mode.ljust(widths['mode'])} | "
        f"{total.rjust(widths['total'])}"
    )


def format_success_response(
    region_group: str,
    ticket_numbers: list[str],
    calculated_results: list[dict],
    target_date: str | None = None,
    lang: str = "en",
) -> str:
    if not calculated_results or not ticket_numbers:
        return t("BET_INVALID_INPUT", lang)

    ticket_no = ticket_numbers[0]
    widths = _build_column_widths(calculated_results, lang)

    header_row = _build_table_header(widths, lang)
    data_rows = [_build_table_row(result, widths) for result in calculated_results]

    ticket_line = f"🎫 : {region_group} · {ticket_no}"
    total_value = sum(
        (result.get("total", Decimal("0")) for result in calculated_results),
        start=Decimal("0"),
    )
    total_line = t("BET_TOTAL_LINE", lang, value=_format_decimal(total_value))

    today = date.today().isoformat()

    body_candidates = [ticket_line, header_row, total_line] + data_rows
    if target_date and target_date != today:
        body_candidates.append(f"📅 : {target_date}")

    divider_len = max(len(line) for line in body_candidates if line)
    thin_divider = "-" * divider_len
    thick_divider = "━" * divider_len

    lines: list[str] = []
    lines.append(t("BET_ACCEPTED", lang))
    lines.append("")
    lines.append(ticket_line)

    if target_date and target_date != today:
        lines.append(f"📅 : {target_date}")

    lines.append(thin_divider)
    lines.append(header_row)
    lines.extend(data_rows)
    lines.append("")
    lines.append(thick_divider)
    lines.append(total_line)

    return "\n".join(lines)
