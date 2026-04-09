from datetime import date
from decimal import Decimal
import re


def _format_decimal(value: Decimal) -> str:
    if value == value.to_integral():
        return str(int(value))
    return format(value.normalize(), "f").rstrip("0").rstrip(".")


def _split_bet_token(bet_token: str) -> tuple[str, str]:
    """
    lo10n -> ("LO", "10N")
    da5k  -> ("DA", "5K")
    xc1n  -> ("XC", "1N")
    """
    token = bet_token.strip()
    match = re.match(r"([a-zA-Z]+)([0-9].*)", token)

    if match:
        return match.group(1).upper(), match.group(2).upper()

    return token.upper(), "-"


def _split_raw_input(raw_input: str) -> tuple[str, str, str, str]:
    """
    Preserve one raw_input as one row.

    Example:
    "dn 11 22 lo10n" -> ("DN", "11 22", "LO", "10N")
    "tp dn 11 23 22 lo10n" -> ("TP DN", "11 23 22", "LO", "10N")
    """
    parts = raw_input.strip().split()

    if len(parts) < 2:
        return "-", raw_input.upper(), "-", "-"

    bet_token = parts[-1]
    body_parts = parts[:-1]
    bet_type, bet_value = _split_bet_token(bet_token)

    mode_tokens: list[str] = []
    number_tokens: list[str] = []

    for token in body_parts:
        if any(ch.isdigit() for ch in token):
            number_tokens.append(token)
        else:
            mode_tokens.append(token.upper())

    mode = " ".join(mode_tokens) if mode_tokens else "-"
    numbers = " ".join(number_tokens) if number_tokens else "-"

    return mode, numbers, bet_type, bet_value


def build_bet_slip_data(
    region_group: str,
    ticket_numbers: list[str],
    calculated_results: list[dict],
    target_date: str | None = None,
) -> dict:
    """
    Convert bet results into Web UI friendly data.

    Output:
    {
        "region": "MN",
        "ticket": "N6",
        "target_date": None,
        "rows": [
            {
                "mode": "DN",
                "numbers": "11 22",
                "type": "LO",
                "bet": "10N",
                "amount": "180",
            }
        ],
        "total": "180",
    }
    """
    if not calculated_results or not ticket_numbers:
        return {
            "region": region_group.upper(),
            "ticket": "-",
            "target_date": target_date,
            "rows": [],
            "total": "0",
        }

    ticket_no = ticket_numbers[0]
    today = date.today().isoformat()

    rows: list[dict] = []
    grand_total = Decimal("0")

    for result in calculated_results:
        raw_input = result["raw_input"]
        amount = result["total"]

        mode, numbers, bet_type, bet_value = _split_raw_input(raw_input)

        rows.append(
            {
                "mode": mode,
                "numbers": numbers,
                "type": bet_type,
                "bet": bet_value,
                "amount": _format_decimal(amount),
            }
        )
        grand_total += amount

    return {
        "region": region_group.upper(),
        "ticket": ticket_no,
        "target_date": target_date if target_date and target_date != today else None,
        "rows": rows,
        "total": _format_decimal(grand_total),
    }