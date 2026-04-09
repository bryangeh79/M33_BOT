from __future__ import annotations

from html import escape
from typing import Any

from src.modules.report.helpers.report_normalizer import ReportNormalizer


def export_over_limit_report_html(data: dict[str, Any]) -> str:
    body_parts: list[str] = []

    body_parts.append("<h1>Over Limit Report</h1>")
    body_parts.append(f"<p><strong>Date:</strong> {escape(str(data['date']))}</p>")

    groups = data.get("groups", {})
    has_any = False

    for region_group in ("MN", "MT", "MB"):
        region_data = groups.get(region_group, {})
        region_html = _render_region_group(region_group, region_data)
        if region_html:
            has_any = True
            body_parts.append(region_html)

    if not has_any:
        body_parts.append("<p>No over limit items.</p>")

    summary = data.get("summary", {})
    body_parts.append("<hr>")
    body_parts.append(
        f"<p><strong>Total Over Limit:</strong> {escape(str(summary.get('total_over_count', 0)))}</p>"
    )

    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Over Limit Report</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 24px;
            color: #222;
        }}
        h1, h2, h3 {{
            margin-bottom: 8px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }}
        th, td {{
            border: 1px solid #ccc;
            padding: 8px 10px;
            text-align: left;
        }}
        th {{
            background: #f5f5f5;
        }}
        .section-title {{
            margin-top: 16px;
            font-size: 18px;
            font-weight: bold;
        }}
        .region-block {{
            margin-bottom: 28px;
        }}
    </style>
</head>
<body>
    {''.join(body_parts)}
</body>
</html>
""".strip()


def _render_region_group(region_group: str, region_data: dict[str, Any]) -> str:
    sections: list[str] = []

    section_2c = _render_normal_section("2c", region_group, region_data.get("2c", {}))
    section_3c = _render_normal_section("3c", region_group, region_data.get("3c", {}))
    section_4c = _render_normal_section("4c", region_group, region_data.get("4c", {}))
    da_section = _render_da_section(region_data.get("da", {}))
    dx_section = _render_dx_section(region_data.get("dx", []))

    if not any([section_2c, section_3c, section_4c, da_section, dx_section]):
        return ""

    sections.append(f"<div class='region-block'><h2>{escape(region_group)}</h2>")
    if section_2c:
        sections.append(section_2c)
    if section_3c:
        sections.append(section_3c)
    if section_4c:
        sections.append(section_4c)
    if da_section:
        sections.append(da_section)
    if dx_section:
        sections.append(dx_section)
    sections.append("</div>")

    return "".join(sections)


def _render_normal_section(
    section_name: str,
    region_group: str,
    section_data: dict[str, list[dict[str, Any]]],
) -> str:
    if not section_data:
        return ""

    parts: list[str] = [f"<div class='section-title'>{escape(section_name)}</div>"]

    if region_group == "MB" and len(section_data) == 1:
        only_region = next(iter(section_data.keys()))
        items = section_data[only_region]

        rows = []
        for item in items:
            rows.append(
                "<tr>"
                f"<td>{escape(str(item['number']))}</td>"
                f"<td>{escape(str(item['play_type']))}</td>"
                f"<td>{escape(ReportNormalizer.format_decimal(item['over_amount']))}</td>"
                "</tr>"
            )

        parts.append(
            "<table>"
            "<thead><tr><th>Number</th><th>Play</th><th>Over</th></tr></thead>"
            f"<tbody>{''.join(rows)}</tbody>"
            "</table>"
        )
        return "".join(parts)

    for region_code in sorted(section_data.keys()):
        rows = []
        for item in section_data[region_code]:
            rows.append(
                "<tr>"
                f"<td>{escape(str(item['number']))}</td>"
                f"<td>{escape(str(item['play_type']))}</td>"
                f"<td>{escape(ReportNormalizer.format_decimal(item['over_amount']))}</td>"
                "</tr>"
            )

        parts.append(f"<h3>{escape(region_code)}</h3>")
        parts.append(
            "<table>"
            "<thead><tr><th>Number</th><th>Play</th><th>Over</th></tr></thead>"
            f"<tbody>{''.join(rows)}</tbody>"
            "</table>"
        )

    return "".join(parts)


def _render_da_section(da_data: dict[str, list[dict[str, Any]]]) -> str:
    if not da_data:
        return ""

    parts: list[str] = ["<div class='section-title'>DA</div>"]

    for region_code in sorted(da_data.keys()):
        rows = []
        for item in da_data[region_code]:
            rows.append(
                "<tr>"
                f"<td>{escape(str(item['number_group']))}</td>"
                f"<td>{escape(ReportNormalizer.format_decimal(item['over_amount']))}</td>"
                "</tr>"
            )

        parts.append(f"<h3>{escape(region_code)}</h3>")
        parts.append(
            "<table>"
            "<thead><tr><th>Number Group</th><th>Over</th></tr></thead>"
            f"<tbody>{''.join(rows)}</tbody>"
            "</table>"
        )

    return "".join(parts)


def _render_dx_section(dx_data: list[dict[str, Any]]) -> str:
    if not dx_data:
        return ""

    rows = []
    for item in dx_data:
        rows.append(
            "<tr>"
            f"<td>{escape(str(item['region_combo']))}</td>"
            f"<td>{escape(str(item['number_group']))}</td>"
            f"<td>{escape(ReportNormalizer.format_decimal(item['over_amount']))}</td>"
            "</tr>"
        )

    return (
        "<div class='section-title'>DX</div>"
        "<table>"
        "<thead><tr><th>Region Combo</th><th>Number Group</th><th>Over</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody>"
        "</table>"
    )