from telegram import KeyboardButton, ReplyKeyboardMarkup

from src.i18n.translator import t


def get_main_menu_button_labels(lang: str = "en") -> list[str]:
    """Return the flat list of main menu button labels for the given language.

    This is the single source of truth for button text AND routing comparison.
    """
    return [
        t("BTN_BET", lang=lang),
        t("BTN_REPORT", lang=lang),
        t("BTN_RESULT", lang=lang),
        t("BTN_OTHER_DAY_INPUT", lang=lang),
        t("BTN_ADMIN", lang=lang),
        t("BTN_INFO", lang=lang),
    ]


def get_main_menu_keyboard(lang: str = "en") -> ReplyKeyboardMarkup:
    """Build the main menu ReplyKeyboard for the given language."""
    btn = lambda key: KeyboardButton(t(key, lang=lang))
    return ReplyKeyboardMarkup(
        [
            [btn("BTN_BET"), btn("BTN_REPORT"), btn("BTN_RESULT")],
            [btn("BTN_OTHER_DAY_INPUT"), btn("BTN_ADMIN"), btn("BTN_INFO")],
        ],
        resize_keyboard=True,
    )
