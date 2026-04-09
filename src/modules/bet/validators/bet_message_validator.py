from datetime import date, datetime
from decimal import Decimal

from src.modules.schedule.validators.schedule_validator import validate_schedule


VALID_PREFIXES_MN = {
    "tg", "kg", "dl", "tp", "dt", "cm", "vt", "bt", "bl", "dn",
    "ct", "st", "tn", "ag", "bth", "bd", "vl", "tv", "la", "bp", "hg"
}

VALID_PREFIXES_MT = {
    "tth", "py", "dla", "qna", "dna", "kh", "bdi", "qtr",
    "qbi", "gl", "nth", "qng", "dno", "kt"
}


def _valid_prefixes(region_group: str):
    region_group = region_group.upper()
    if region_group == "MN":
        return VALID_PREFIXES_MN
    if region_group == "MT":
        return VALID_PREFIXES_MT
    return set()


def _normalize_target_date(target_date) -> date:
    if isinstance(target_date, date):
        return target_date

    if isinstance(target_date, str):
        return datetime.strptime(target_date, "%Y-%m-%d").date()

    return date.today()


def validate_bet(
    parsed_bet: dict,
    region_group: str,
    target_date=None,
) -> tuple[bool, str | None, None]:
    """
    Validate a single parsed bet entry.

    Returns a 3-tuple: (valid, error_code, None)

    error_code values:
        None            — success
        "INVALID_INPUT" — format / value / structure error
        "SCHEDULE_CLOSED" — region not open for the target date
    """
    region_group = region_group.upper()
    target_date_obj = _normalize_target_date(target_date)

    if not parsed_bet.get("valid_structure"):
        return False, "INVALID_INPUT", None

    bet_type = str(parsed_bet.get("type", "")).lower()
    amount = parsed_bet.get("amount", Decimal("0"))

    if bet_type not in {"lo", "dd", "xc", "da", "dx"}:
        return False, "INVALID_INPUT", None

    if not isinstance(amount, Decimal):
        return False, "INVALID_INPUT", None

    if amount <= 0:
        return False, "INVALID_INPUT", None

    # MB special rules
    if region_group == "MB":
        if bet_type == "dx":
            return False, "INVALID_INPUT", None

        if bet_type == "da":
            numbers = parsed_bet.get("numbers", [])
            if not isinstance(numbers, list) or len(numbers) < 2:
                return False, "INVALID_INPUT", None

            for number in numbers:
                number = str(number)
                if not number.isdigit() or len(number) != 2:
                    return False, "INVALID_INPUT", None

            if len(set(numbers)) != len(numbers):
                return False, "INVALID_INPUT", None

            return True, None, None

        number = str(parsed_bet.get("number", ""))
        if not number.isdigit():
            return False, "INVALID_INPUT", None

        digits = len(number)
        if digits not in (2, 3, 4):
            return False, "INVALID_INPUT", None

        if bet_type == "dd" and digits != 2:
            return False, "INVALID_INPUT", None

        if bet_type == "xc" and digits not in (3, 4):
            return False, "INVALID_INPUT", None

        return True, None, None

    # MN / MT
    valid_prefixes = _valid_prefixes(region_group)

    if bet_type == "da":
        prefix = str(parsed_bet.get("prefix", "")).lower()
        numbers = parsed_bet.get("numbers", [])

        if prefix not in valid_prefixes:
            return False, "INVALID_INPUT", None

        schedule_result = validate_schedule(region_group, prefix, target_date_obj)
        if not schedule_result.is_allowed:
            return False, "SCHEDULE_CLOSED", None

        if not isinstance(numbers, list) or len(numbers) < 2:
            return False, "INVALID_INPUT", None

        for number in numbers:
            number = str(number)
            if not number.isdigit() or len(number) != 2:
                return False, "INVALID_INPUT", None

        if len(set(numbers)) != len(numbers):
            return False, "INVALID_INPUT", None

        return True, None, None

    if bet_type == "dx":
        prefixes = parsed_bet.get("prefixes", [])
        numbers = parsed_bet.get("numbers", [])

        if not isinstance(prefixes, list) or len(prefixes) < 2:
            return False, "INVALID_INPUT", None

        for prefix in prefixes:
            normalized_prefix = str(prefix).lower()

            if normalized_prefix not in valid_prefixes:
                return False, "INVALID_INPUT", None

            schedule_result = validate_schedule(region_group, normalized_prefix, target_date_obj)
            if not schedule_result.is_allowed:
                return False, "SCHEDULE_CLOSED", None

        if len(set(prefixes)) != len(prefixes):
            return False, "INVALID_INPUT", None

        if not isinstance(numbers, list) or len(numbers) < 2:
            return False, "INVALID_INPUT", None

        for number in numbers:
            number = str(number)
            if not number.isdigit() or len(number) != 2:
                return False, "INVALID_INPUT", None

        if len(set(numbers)) != len(numbers):
            return False, "INVALID_INPUT", None

        return True, None, None

    # LO / DD / XC
    prefix = str(parsed_bet.get("prefix", "")).lower()
    number = str(parsed_bet.get("number", ""))

    if prefix not in valid_prefixes:
        return False, "INVALID_INPUT", None

    schedule_result = validate_schedule(region_group, prefix, target_date_obj)
    if not schedule_result.is_allowed:
        return False, "SCHEDULE_CLOSED", None

    if not number.isdigit():
        return False, "INVALID_INPUT", None

    digits = len(number)
    if digits not in (2, 3, 4):
        return False, "INVALID_INPUT", None

    if bet_type == "dd" and digits != 2:
        return False, "INVALID_INPUT", None

    if bet_type == "xc" and digits not in (3, 4):
        return False, "INVALID_INPUT", None

    return True, None, None
