"""
report_constants.py

Non-user-visible callback/type identifiers are plain constants (never change
with language).

User-visible label constants remain English strings for backward compatibility
with code that imports them directly.  For language-aware label access, call
get_report_labels(lang) which delegates to the i18n layer.
"""

from src.i18n.translator import t

# ── Report type identifiers (internal, not user-visible) ──────────────────
REPORT_TYPE_TRANSACTION  = "transaction"
REPORT_TYPE_SETTLEMENT   = "settlement"
REPORT_TYPE_NUMBER_DETAIL = "number_detail"
REPORT_TYPE_OVER_LIMIT   = "over_limit"

# ── Callback data keys (internal, not user-visible) ───────────────────────
REPORT_CALLBACK_MENU         = "report:menu"
REPORT_CALLBACK_CLOSE        = "report:close"
REPORT_CALLBACK_BACK_TO_MENU = "report:back"
REPORT_CALLBACK_TYPE_PREFIX  = "report:type:"
REPORT_CALLBACK_DATE_PREFIX  = "report:date:"
REPORT_CALLBACK_EXPORT_PREFIX = "report:export:"

# ── Data constants (not user-visible) ─────────────────────────────────────
REPORT_REGION_GROUPS  = ["MN", "MT", "MB"]
REPORT_BET_TYPE_ORDER = ["LO", "DA", "DX", "2C", "3C", "4C"]
DIVIDER = "━━━━━━━━━━━━"

# ── User-visible label constants (English, backward-compat) ───────────────
# These are kept as plain strings so existing imports continue to work.
# Do NOT replace them with t(...) at module level — that would lock the
# language at import time and break future per-session language switching.
REPORT_MENU_TITLE         = "Report"
REPORT_LABEL_TRANSACTION  = "Transaction"
REPORT_LABEL_SETTLEMENT   = "Settlement"
REPORT_LABEL_NUMBER_DETAIL = "Number Detail"
REPORT_LABEL_OVER_LIMIT   = "Over Limit"
REPORT_COMING_SOON_TEXT   = "Coming Soon"
REPORT_NO_DATA_TEXT       = "No data available."


def get_report_labels(lang: str = "en") -> dict[str, str]:
    """Return all user-visible report labels for the given language.

    This is the i18n-aware path.  Use this when you need labels that reflect
    the active session language rather than the module-level English defaults.

    Returns a dict with keys:
        menu_title, transaction, settlement, number_detail,
        over_limit, coming_soon, no_data
    """
    return {
        "menu_title":    t("REPORT_MENU_TITLE",         lang),
        "transaction":   t("REPORT_LABEL_TRANSACTION",   lang),
        "settlement":    t("REPORT_LABEL_SETTLEMENT",    lang),
        "number_detail": t("REPORT_LABEL_NUMBER_DETAIL", lang),
        "over_limit":    t("REPORT_LABEL_OVER_LIMIT",    lang),
        "coming_soon":   t("REPORT_COMING_SOON",         lang),
        "no_data":       t("REPORT_NO_DATA",             lang),
    }
