from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import Any

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


def _generated_at_utc8() -> str:
    tz = timezone(timedelta(hours=8))
    return datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")


def _fmt_amount(value: Any) -> str:
    return ReportNormalizer.format_decimal(value)


def _build_table(rows: list[dict[str, str]]) -> list[str]:
    region_w = max(len("Region"), max((len(r["region"]) for r in rows), default=6))
    number_w = max(len("Number"), max((len(r["number"]) for r in rows), default=6))
    mode_w = max(len("Mode"), max((len(r["mode"]) for r in rows), default=4))
    total_w = max(len("Total"), max((len(r["total"]) for r in rows), default=5))

    lines = [
        f"{'Region'.ljust(region_w)}  {'Number'.ljust(number_w)}  {'Mode'.ljust(mode_w)}  {'Total'.rjust(total_w)}"
    ]

    for row in rows:
        lines.append(
            f"{row['region'].ljust(region_w)}  "
            f"{row['number'].ljust(number_w)}  "
            f"{row['mode'].ljust(mode_w)}  "
            f"{row['total'].rjust(total_w)}"
        )

    return lines


def _collect_region_rows(region_data: dict[str, Any]) -> dict[tuple[str, str], list[dict[str, str]]]:
    grouped: dict[tuple[str, str], list[dict[str, str]]] = {}

    # 2C LO / DD
    section_2c = region_data.get("2c", {}) or {}
    for region_code, items in section_2c.items():
        for item in items:
            mode = str(item.get("play_type", "")).upper().strip()
            key = ("2C", mode)
            grouped.setdefault(key, []).append(
                {
                    "region": str(region_code).lower(),
                    "number": str(item.get("number", "")).strip(),
                    "mode": mode,
                    "total": _fmt_amount(item.get("over_amount", 0)),
                }
            )

    # 2C DA
    da_data = region_data.get("da", {}) or {}
    for region_code, items in da_data.items():
        for item in items:
            key = ("2C", "DA")
            grouped.setdefault(key, []).append(
                {
                    "region": str(region_code).lower(),
                    "number": str(item.get("number_group", "")).strip(),
                    "mode": "DA",
                    "total": _fmt_amount(item.get("over_amount", 0)),
                }
            )

    # 2C DX
    dx_data = region_data.get("dx", []) or []
    for item in dx_data:
        key = ("2C", "DX")
        grouped.setdefault(key, []).append(
            {
                "region": str(item.get("region_combo", "")).lower(),
                "number": str(item.get("number_group", "")).strip(),
                "mode": "DX",
                "total": _fmt_amount(item.get("over_amount", 0)),
            }
        )

    # 3C
    section_3c = region_data.get("3c", {}) or {}
    for region_code, items in section_3c.items():
        for item in items:
            mode = str(item.get("play_type", "")).upper().strip()
            key = ("3C", mode)
            grouped.setdefault(key, []).append(
                {
                    "region": str(region_code).lower(),
                    "number": str(item.get("number", "")).strip(),
                    "mode": mode,
                    "total": _fmt_amount(item.get("over_amount", 0)),
                }
            )

    # 4C
    section_4c = region_data.get("4c", {}) or {}
    for region_code, items in section_4c.items():
        for item in items:
            mode = str(item.get("play_type", "")).upper().strip()
            key = ("4C", mode)
            grouped.setdefault(key, []).append(
                {
                    "region": str(region_code).lower(),
                    "number": str(item.get("number", "")).strip(),
                    "mode": mode,
                    "total": _fmt_amount(item.get("over_amount", 0)),
                }
            )

    for key, rows in grouped.items():
        rows.sort(key=lambda x: (x["region"], x["number"], x["mode"]))

    return grouped


def format_over_limit_report(data: dict[str, Any]) -> str:
    target_date = str(data.get("date", "")).strip()
    groups = data.get("groups", {}) or {}
    generated_at = _generated_at_utc8()

    lines: list[str] = []
    lines.append("⚠️ Over Limit Report")
    lines.append(f"📅 : {target_date}")
    lines.append("")

    first_region = True

    for region_group in ("MN", "MT", "MB"):
        region_data = groups.get(region_group, {}) or {}
        grouped = _collect_region_rows(region_data)

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
                lines.extend(_build_table(rows))
                lines.append("")
                has_any_data = True

        if not has_any_data:
            lines.append("No data")

    while lines and lines[-1] == "":
        lines.pop()

    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━━━")
    lines.append(f"🕒 Generated at: {generated_at} (UTC+8)")

    return "\n".join(lines)
