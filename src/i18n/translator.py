"""
translator.py — unified i18n entry point.

Usage:
    from src.i18n.translator import t

    t("BTN_BACK")                      # English default
    t("BTN_BACK", lang="vi")           # Vietnamese
    t("BTN_TODAY", date="02/04")       # template substitution
    t("INFO_VERSION", version="1.387") # template substitution

Rules:
- Default lang is "en".
- If the key is missing in the requested language, falls back to "en".
- If the key is missing in "en" too, returns the key itself as-is.
- Supports {variable} template substitution via kwargs.
- Unknown lang codes fall back to "en".
"""

from src.i18n import en, zh, vi

_LANGS: dict[str, dict[str, str]] = {
    "en": en.STRINGS,
    "zh": zh.STRINGS,
    "vi": vi.STRINGS,
}

_DEFAULT_LANG = "en"


def t(key: str, lang: str = _DEFAULT_LANG, **kwargs) -> str:
    """Look up a translation key and optionally apply template substitution.

    Args:
        key:    The i18n key (e.g. "BTN_BACK", "PROMPT_SELECT_DATE").
        lang:   Language code: "en" | "zh" | "vi". Defaults to "en".
        **kwargs: Named values substituted into {placeholder} in the string.

    Returns:
        Translated string, or the key itself if not found anywhere.
    """
    strings = _LANGS.get(lang, _LANGS[_DEFAULT_LANG])

    text = strings.get(key)
    if text is None:
        text = _LANGS[_DEFAULT_LANG].get(key, key)

    if kwargs and text:
        try:
            text = text.format(**kwargs)
        except (KeyError, ValueError):
            pass

    return text
