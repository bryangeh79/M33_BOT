import re
from decimal import Decimal


MN_PREFIXES = {
    "tg", "kg", "dl", "tp", "dt", "cm", "vt", "bt", "bl", "dn",
    "ct", "st", "tn", "ag", "bth", "bd", "vl", "tv", "la", "bp", "hg"
}

MT_PREFIXES = {
    "tth", "py", "dla", "qna", "dna", "kh", "bdi", "qtr",
    "qbi", "gl", "nth", "qng", "dno", "kt"
}


def _group_prefixes(region_group: str):
    region_group = region_group.upper()
    if region_group == "MN":
        return MN_PREFIXES
    if region_group == "MT":
        return MT_PREFIXES
    return set()


def _normalize_lines(text: str):
    """
    把 Telegram 发来的文本强制标准化成多行列表
    """
    if not text:
        return []

    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.strip()

    if not text:
        return []

    lines = []
    for raw_line in text.split("\n"):
        line = raw_line.strip().lower()
        line = re.sub(r"\s+", " ", line)
        if line:
            lines.append(line)

    return lines


def _format_amount_text(amount: Decimal) -> str:
    """
    避免 Decimal('10').normalize() 变成 1E+1
    """
    if amount == amount.to_integral():
        return str(int(amount))
    return format(amount.normalize(), "f").rstrip("0").rstrip(".")


def _build_display_mode(bet_type: str, amount: Decimal) -> str:
    bet_type = str(bet_type).lower().strip()

    # DA / DX 不带金额展示
    if bet_type in {"da", "dx"}:
        return bet_type.upper()

    amount_text = _format_amount_text(amount)
    return f"{bet_type}{amount_text}n".upper()


def parse_bet_message(text: str, region_group: str):
    """
    解析投注消息

    支持：
    - MN / MT:
      1) LO / DD / XC:
         区域 [多个区域] 号码 [多个号码] 玩法金额

      2) DA:
         单区域 号码 [多个号码] da金额

      3) DX:
         多区域 号码 [多个号码] dx金额

    - MB:
      1) LO / DD / XC:
         号码 [多个号码] 玩法金额
         或
         mb 号码 [多个号码] 玩法金额

      2) DA:
         号码 [多个号码] da金额
         或
         mb 号码 [多个号码] da金额

      3) DX:
         不允许
    """

    region_group = region_group.upper()
    lines = _normalize_lines(text)

    if not lines:
        return []

    parsed_results = []

    final_token_pattern = re.compile(r"^(lo|dd|xc|da|dx)(\d+(?:\.\d+)?)n$")

    for line in lines:
        tokens = line.split()

        if len(tokens) < 2:
            parsed_results.append({
                "source_line": line,
                "raw_input": line,
                "valid_structure": False,
            })
            continue

        last_token = tokens[-1]
        final_match = final_token_pattern.match(last_token)

        if not final_match:
            parsed_results.append({
                "source_line": line,
                "raw_input": line,
                "valid_structure": False,
            })
            continue

        bet_type = final_match.group(1)
        amount = Decimal(final_match.group(2))
        display_mode = _build_display_mode(bet_type, amount)
        middle_tokens = tokens[:-1]

        if region_group in {"MN", "MT"}:
            valid_prefixes = _group_prefixes(region_group)

            if bet_type == "da":
                # DA: 单区域 + 多号码
                if len(middle_tokens) < 3:
                    parsed_results.append({
                        "source_line": line,
                        "raw_input": line,
                        "valid_structure": False,
                    })
                    continue

                prefix = middle_tokens[0]
                number_tokens = middle_tokens[1:]

                if prefix not in valid_prefixes:
                    parsed_results.append({
                        "source_line": line,
                        "raw_input": line,
                        "valid_structure": False,
                    })
                    continue

                if not number_tokens or any(not token.isdigit() for token in number_tokens):
                    parsed_results.append({
                        "source_line": line,
                        "raw_input": line,
                        "valid_structure": False,
                    })
                    continue

                parsed_results.append({
                    "source_line": line,
                    "raw_input": line,
                    "display_raw_input": f"{prefix} {' '.join(number_tokens)} {display_mode.lower()}",
                    "display_mode": display_mode,
                    "group_numbers": number_tokens[:],
                    "valid_structure": True,
                    "prefix": prefix,
                    "numbers": number_tokens,
                    "type": bet_type,
                    "amount": amount,
                })
                continue

            prefixes = []
            numbers = []
            number_section_started = False
            structure_invalid = False

            for token in middle_tokens:
                if token.isdigit():
                    number_section_started = True
                    numbers.append(token)
                else:
                    if number_section_started:
                        structure_invalid = True
                        break
                    if token not in valid_prefixes:
                        structure_invalid = True
                        break
                    prefixes.append(token)

            if structure_invalid or not prefixes or not numbers:
                parsed_results.append({
                    "source_line": line,
                    "raw_input": line,
                    "valid_structure": False,
                })
                continue

            if bet_type == "dx":
                parsed_results.append({
                    "source_line": line,
                    "raw_input": line,
                    "display_raw_input": f"{' '.join(prefixes)} {' '.join(numbers)} {display_mode.lower()}",
                    "display_mode": display_mode,
                    "group_numbers": numbers[:],
                    "valid_structure": True,
                    "prefixes": prefixes,
                    "numbers": numbers,
                    "type": bet_type,
                    "amount": amount,
                })
                continue

            # LO / DD / XC：区域 × 号码
            # 仍然拆开给 calculator / DB 用，但额外保留 group_numbers + display_mode
            for prefix in prefixes:
                for number in numbers:
                    parsed_results.append({
                        "source_line": line,
                        "raw_input": f"{prefix} {number} {bet_type}{_format_amount_text(amount)}n",
                        "display_raw_input": f"{prefix} {' '.join(numbers)} {display_mode.lower()}",
                        "display_mode": display_mode,
                        "group_numbers": numbers[:],
                        "valid_structure": True,
                        "prefix": prefix,
                        "number": number,
                        "type": bet_type,
                        "amount": amount,
                    })

        elif region_group == "MB":
            if not middle_tokens:
                parsed_results.append({
                    "source_line": line,
                    "raw_input": line,
                    "valid_structure": False,
                })
                continue

            if middle_tokens[0] == "mb":
                middle_tokens = middle_tokens[1:]

            if not middle_tokens:
                parsed_results.append({
                    "source_line": line,
                    "raw_input": line,
                    "valid_structure": False,
                })
                continue

            if any(not token.isdigit() for token in middle_tokens):
                parsed_results.append({
                    "source_line": line,
                    "raw_input": line,
                    "valid_structure": False,
                })
                continue

            numbers = middle_tokens

            if bet_type == "dx":
                parsed_results.append({
                    "source_line": line,
                    "raw_input": line,
                    "valid_structure": False,
                })
                continue

            if bet_type == "da":
                parsed_results.append({
                    "source_line": line,
                    "raw_input": line,
                    "display_raw_input": f"mb {' '.join(numbers)} {display_mode.lower()}",
                    "display_mode": display_mode,
                    "group_numbers": numbers[:],
                    "valid_structure": True,
                    "prefix": "mb",
                    "numbers": numbers,
                    "type": bet_type,
                    "amount": amount,
                })
                continue

            for number in numbers:
                parsed_results.append({
                    "source_line": line,
                    "raw_input": f"{number} {bet_type}{_format_amount_text(amount)}n",
                    "display_raw_input": f"mb {' '.join(numbers)} {display_mode.lower()}",
                    "display_mode": display_mode,
                    "group_numbers": numbers[:],
                    "valid_structure": True,
                    "prefix": "mb",
                    "number": number,
                    "type": bet_type,
                    "amount": amount,
                })
        else:
            parsed_results.append({
                "source_line": line,
                "raw_input": line,
                "valid_structure": False,
            })

    return parsed_results