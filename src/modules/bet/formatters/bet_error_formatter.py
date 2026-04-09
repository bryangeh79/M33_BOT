from src.i18n.translator import t


def format_error_response(error_lines, lang: str = "en"):
    """
    错误格式：
    原输入行 Invalid Input

    error_lines: list[str]
    """
    if not error_lines:
        return t("BET_INVALID_INPUT", lang)

    return "\n".join(error_lines)
