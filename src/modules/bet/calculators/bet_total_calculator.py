from decimal import Decimal


def calculate_total(parsed_bet: dict, region_group: str):
    """
    计算单行投注 total
    支持：
    - MN / MT / MB
    - LO / DD / XC / DA / DX
    """

    region_group = region_group.upper()
    bet_type = str(parsed_bet["type"]).lower()
    amount = parsed_bet["amount"]

    # DA
    if bet_type == "da":
        numbers = parsed_bet["numbers"]
        group_count = len(numbers) * (len(numbers) - 1) // 2

        if region_group in {"MN", "MT"}:
            multiplier = Decimal("36")
        elif region_group == "MB":
            multiplier = Decimal("54")
        else:
            raise ValueError("Invalid region group for DA")

        total = amount * multiplier * Decimal(str(group_count))

        return {
            "raw_input": parsed_bet["raw_input"],
            "prefix": parsed_bet.get("prefix", "mb"),
            "numbers": numbers,
            "number": " ".join(numbers),
            "type": bet_type,
            "amount": amount,
            "multiplier": multiplier,
            "group_count": group_count,
            "total": total,
        }

    # DX
    if bet_type == "dx":
        if region_group == "MB":
            raise ValueError("DX not allowed in MB")

        prefixes = parsed_bet["prefixes"]
        numbers = parsed_bet["numbers"]

        region_group_count = len(prefixes) * (len(prefixes) - 1) // 2
        number_group_count = len(numbers) * (len(numbers) - 1) // 2
        multiplier = Decimal("72")

        total = (
            amount
            * multiplier
            * Decimal(str(region_group_count))
            * Decimal(str(number_group_count))
        )

        return {
            "raw_input": parsed_bet["raw_input"],
            "prefix": ",".join(prefixes),
            "prefixes": prefixes,
            "numbers": numbers,
            "number": " ".join(numbers),
            "type": bet_type,
            "amount": amount,
            "multiplier": multiplier,
            "region_group_count": region_group_count,
            "number_group_count": number_group_count,
            "total": total,
        }

    # LO / DD / XC
    number = str(parsed_bet["number"])
    digits = len(number)

    if bet_type == "lo":
        if region_group in {"MN", "MT"}:
            if digits == 2:
                multiplier = Decimal("18")
            elif digits == 3:
                multiplier = Decimal("17")
            elif digits == 4:
                multiplier = Decimal("16")
            else:
                raise ValueError("Invalid LO digit length")
        elif region_group == "MB":
            if digits == 2:
                multiplier = Decimal("27")
            elif digits == 3:
                multiplier = Decimal("23")
            elif digits == 4:
                multiplier = Decimal("20")
            else:
                raise ValueError("Invalid LO digit length")
        else:
            raise ValueError("Invalid region group")

    elif bet_type == "dd":
        if digits != 2:
            raise ValueError("DD only accepts 2-digit numbers")

        if region_group in {"MN", "MT"}:
            multiplier = Decimal("2")
        elif region_group == "MB":
            multiplier = Decimal("5")
        else:
            raise ValueError("Invalid region group")

    elif bet_type == "xc":
        if digits not in (3, 4):
            raise ValueError("XC only accepts 3-digit or 4-digit numbers")

        if region_group in {"MN", "MT"}:
            multiplier = Decimal("2")
        elif region_group == "MB":
            multiplier = Decimal("4")
        else:
            raise ValueError("Invalid region group")

    else:
        raise ValueError("Unsupported bet type")

    total = amount * multiplier

    return {
        "raw_input": parsed_bet["raw_input"],
        "prefix": parsed_bet["prefix"],
        "number": number,
        "type": bet_type,
        "amount": amount,
        "multiplier": multiplier,
        "total": total,
    }