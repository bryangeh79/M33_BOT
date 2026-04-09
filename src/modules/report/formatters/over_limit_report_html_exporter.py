from __future__ import annotations

from datetime import datetime, timezone, timedelta
from html import escape
from typing import Any

from src.i18n.translator import t
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


def _collect_region_rows(region_data: dict[str, Any]) -> dict[tuple[str, str], list[dict[str, str]]]:
    grouped: dict[tuple[str, str], list[dict[str, str]]] = {}

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
                    "over": _fmt_amount(item.get("over_amount", 0)),
                }
            )

    da_data = region_data.get("da", {}) or {}
    for region_code, items in da_data.items():
        for item in items:
            key = ("2C", "DA")
            grouped.setdefault(key, []).append(
                {
                    "region": str(region_code).lower(),
                    "number": str(item.get("number_group", "")).strip(),
                    "mode": "DA",
                    "over": _fmt_amount(item.get("over_amount", 0)),
                }
            )

    dx_data = region_data.get("dx", []) or []
    for item in dx_data:
        key = ("2C", "DX")
        grouped.setdefault(key, []).append(
            {
                "region": str(item.get("region_combo", "")).lower(),
                "number": str(item.get("number_group", "")).strip(),
                "mode": "DX",
                "over": _fmt_amount(item.get("over_amount", 0)),
            }
        )

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
                    "over": _fmt_amount(item.get("over_amount", 0)),
                }
            )

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
                    "over": _fmt_amount(item.get("over_amount", 0)),
                }
            )

    for key, rows in grouped.items():
        rows.sort(key=lambda x: (x["region"], x["number"], x["mode"]))

    return grouped


def _build_table(rows: list[dict[str, str]], lang: str = "en") -> str:
    row_html = "".join(
        f"""
        <tr>
            <td>{escape(row['region'])}</td>
            <td>{escape(row['number'])}</td>
            <td>{escape(row['mode'])}</td>
            <td class="num">{escape(row['over'])}</td>
        </tr>
        """
        for row in rows
    )

    return f"""
    <table>
        <thead>
            <tr>
                <th>{escape(t('COL_REGION', lang=lang))}</th>
                <th>{escape(t('COL_NUMBER', lang=lang))}</th>
                <th>{escape(t('COL_MODE', lang=lang))}</th>
                <th class="num">Over</th>
            </tr>
        </thead>
        <tbody>
            {row_html}
        </tbody>
    </table>
    """


def export_over_limit_report_html(data: dict[str, Any], lang: str = "en") -> str:
    target_date = escape(str(data.get("date", "")).strip())
    groups = data.get("groups", {}) or {}
    generated_at = _generated_at_utc8()

    sections: list[str] = []

    for region_group in ("MN", "MT", "MB"):
        region_data = groups.get(region_group, {}) or {}
        grouped = _collect_region_rows(region_data)

        blocks: list[str] = []

        for section_name, mode_list in SECTION_ORDER:
            mode_blocks: list[str] = []

            for mode in mode_list:
                rows = grouped.get((section_name, mode), [])
                if not rows:
                    continue

                mode_blocks.append(
                    f"""
                    <div class="mode-block">
                        <div class="mode-title">{escape(SECTION_TITLE_MAP[(section_name, mode)])}</div>
                        {_build_table(rows, lang=lang)}
                    </div>
                    """
                )

            if mode_blocks:
                blocks.append(
                    f"""
                    <div class="section-block">
                        <div class="section-title">{escape(section_name.lower())}</div>
                        {''.join(mode_blocks)}
                    </div>
                    """
                )

        if not blocks:
            content = f'<div class="no-data">{escape(t("REPORT_NO_DATA", lang=lang))}</div>'
        else:
            content = "".join(blocks)

        sections.append(
            f"""
            <section class="region-card">
                <h2>{escape(region_group)}</h2>
                {content}
            </section>
            """
        )

    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <title>{escape(t('REPORT_OVER_LIMIT_TITLE', lang=lang))} {target_date}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 24px;
            color: #222;
            background: #fff;
        }}
        h1 {{
            margin-bottom: 6px;
        }}
        .meta {{
            margin-bottom: 18px;
            color: #555;
        }}
        .region-card {{
            border: 1px solid #ddd;
            border-radius: 10px;
            padding: 16px;
            margin-bottom: 18px;
        }}
        .section-title {{
            font-size: 18px;
            font-weight: 700;
            text-transform: lowercase;
            margin: 14px 0 8px;
        }}
        .mode-block {{
            margin-bottom: 14px;
        }}
        .mode-title {{
            font-weight: 700;
            margin-bottom: 6px;
        }}
        .no-data {{
            color: #666;
            font-style: italic;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 8px;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        th {{
            background: #f5f5f5;
        }}
        td.num, th.num {{
            text-align: right;
        }}
        .footer {{
            margin-top: 20px;
            padding-top: 12px;
            border-top: 1px solid #ddd;
            color: #666;
            font-size: 13px;
        }}
    </style>
</head>
<body>
    <h1>{escape(t('REPORT_OVER_LIMIT_TITLE', lang=lang))}</h1>
    <div class="meta">{escape(t('REPORT_DATE_LABEL', lang=lang, date=target_date))}</div>
    {''.join(sections)}
    <div class="footer">{escape(t('REPORT_GENERATED_AT', lang=lang, ts=generated_at))}</div>
</body>
</html>
""".strip()
