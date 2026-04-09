from src.bot.menus.main_menu import get_main_menu_keyboard


def get_main_menu(lang: str = "en"):
    """Thin wrapper — delegates to the single source in main_menu.py."""
    return get_main_menu_keyboard(lang=lang)
