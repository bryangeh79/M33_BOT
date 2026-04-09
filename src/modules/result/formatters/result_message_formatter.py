from __future__ import annotations

from collections import defaultdict
from typing import Dict, List

from src.i18n.translator import t

DIVIDER = "━━━━━━━━━━━━"


def _format_fetched_ts(fetched_at: str | None, lang: str = "en") -> str:
    if not fetched_at:
        return ""
    ts = fetched_at.strip()
    if len(ts) >= 16:
        ts = ts[:16]
    return f"\n{t('RESULT_FETCHED_LABEL', lang)} {ts}"


def format_result_message(meta: Dict | None, items: List[Dict], lang: str = "en") -> str:
    meta = meta or {}

    region = (meta.get("region_code") or "").upper()
    date = meta.get("draw_date") or ""
    status = (meta.get("status") or "").lower()

    title = t("RESULT_TITLE", lang)
    date_label = t("RESULT_DATE_LABEL", lang)

    if status != "available" or not items:
        return f"{title} | {region}\n{date_label} {date}\n\n{t('RESULT_NOT_AVAILABLE', lang)}"

    fetched_line = _format_fetched_ts(meta.get("fetched_at"), lang)
    header = f"{title} | {region}\n{date_label} {date}{fetched_line}"

    # Group by sub-region while preserving incoming order
    blocks: Dict[str, Dict] = {}

    for it in items:
        sub_code = it["sub_region_code"]
        sub_name = it["sub_region_name"]
        prize_code = it["prize_code"]
        prize_order = int(it.get("prize_order", 999))
        item_order = int(it.get("item_order", 999))
        number = it["number_value"]

        if sub_code not in blocks:
            blocks[sub_code] = {
                "name": sub_name,
                "prizes": defaultdict(list),
            }

        blocks[sub_code]["prizes"][prize_order].append(
            (item_order, prize_code, number)
        )

    lines: List[str] = [header]

    first_block = True
    for _, data in blocks.items():
        name = data["name"]

        if first_block:
            lines.append("")
            first_block = False
        else:
            lines.append("")
            lines.append("")

        lines.append(DIVIDER)
        lines.append(f"📍 {name}")

        for p_order in sorted(data["prizes"].keys()):
            entries = sorted(data["prizes"][p_order], key=lambda t: t[0])
            if not entries:
                continue

            prize_code = entries[0][1]
            numbers = [e[2] for e in entries]
            lines.append(f"{prize_code} : {'  '.join(numbers)}")

    return "\n".join(lines)
