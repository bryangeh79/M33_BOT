import os
import re
import sys
from datetime import datetime, timedelta, date
from html import escape
from pathlib import Path

from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from src.bot.menus.bet_menu import get_bet_menu_keyboard
from src.bot.menus.main_menu import get_main_menu_keyboard
from src.modules.admin.services.admin_auth_service import AdminAuthService
from src.modules.admin.services.admin_settings_service import AdminSettingsService
from src.modules.bet.services.bet_message_service import (
    process_bet_message,
    init_database,
    delete_ticket,
)
from src.modules.customer.repositories.agent_customer_repository import AgentCustomerRepository
from src.modules.report.constants.report_constants import (
    REPORT_CALLBACK_BACK_TO_MENU,
    REPORT_CALLBACK_CLOSE,
    REPORT_CALLBACK_DATE_PREFIX,
    REPORT_CALLBACK_EXPORT_PREFIX,
    REPORT_CALLBACK_MENU,
    REPORT_CALLBACK_TYPE_PREFIX,
    REPORT_COMING_SOON_TEXT,
    REPORT_LABEL_NUMBER_DETAIL,
    REPORT_LABEL_OVER_LIMIT,
    REPORT_LABEL_SETTLEMENT,
    REPORT_LABEL_TRANSACTION,
    REPORT_MENU_TITLE,
    REPORT_TYPE_NUMBER_DETAIL,
    REPORT_TYPE_OVER_LIMIT,
    REPORT_TYPE_SETTLEMENT,
    REPORT_TYPE_TRANSACTION,
)
from src.modules.schedule.constants.region_schedule_map import get_allowed_regions
from src.modules.report.formatters.number_detail_report_formatter import (
    format_report as format_number_detail_report,
)
from src.modules.report.formatters.over_limit_report_formatter import (
    format_over_limit_report,
)
from src.modules.report.formatters.over_limit_report_html_exporter import (
    export_over_limit_report_html,
)
from src.modules.report.formatters.report_html_formatter import (
    build_number_detail_report_html,
    build_transaction_report_html,
)
from src.modules.report.formatters.settlement_report_formatter import (
    format_settlement_report_telegram,
)
from src.modules.report.formatters.settlement_report_html_exporter import (
    export_settlement_report_html,
)
from src.modules.report.formatters.transaction_report_formatter import (
    format_report as format_transaction_report,
)
from src.modules.report.helpers.report_normalizer import ReportNormalizer
from src.modules.report.services.number_detail_report_service import (
    NumberDetailReportService,
)
from src.modules.report.services.over_limit_report_service import (
    OverLimitReportService,
)
from src.modules.report.services.settlement_report_service import (
    SettlementReportService,
)
from src.modules.report.services.transaction_report_service import (
    TransactionReportService,
)
from src.modules.result.constants.result_constants import (
    CALLBACK_RESULT_CHANGE_DATE,
    CALLBACK_RESULT_CLOSE,
    CALLBACK_RESULT_DATE_PREFIX,
    CALLBACK_RESULT_MENU,
    CALLBACK_RESULT_REFRESH_PREFIX,
    CALLBACK_RESULT_VIEW_PREFIX,
)
from src.modules.result.formatters.result_message_formatter import format_result_message
from src.modules.result.services.result_fetch_service import ResultFetchService
from src.modules.result.services.result_query_service import ResultQueryService

load_dotenv()

# =========================================================
# Phase 1.1: Unified State Definitions
# =========================================================
class UserState:
    """Minimal state machine for ReplyKeyboard routing.

    States replace scattered boolean flags (waiting_custom_date, region, etc.)
    with a single `state` field in user_context.

    Transitions:
        IDLE → BET_REGION          (user taps "Bet")
        BET_REGION → BET_INPUT     (user taps MN/MT/MB)
        BET_INPUT → IDLE           (user taps main menu button)
        IDLE → ODI_DATE            (user taps "Other Day Input")
        ODI_DATE → BET_REGION      (user picks date)
        IDLE → RESULT_DATE         (user taps "Result")
        RESULT_DATE → RESULT_REGION (user picks date)
        RESULT_REGION → IDLE       (user views result / back)
        IDLE → ADMIN_MENU          (user taps "Admin")
        ADMIN_MENU → IDLE          (user taps "⬅ Back")
        * → IDLE                   (default fallback / menu button tap)
    """
    IDLE = "idle"                       # Main menu visible
    BET_REGION = "bet_region"           # Selecting MN/MT/MB
    BET_INPUT = "bet_input"             # Typing bets
    ODI_DATE = "odi_date"              # Selecting date for Other Day Input
    REPORT_TYPE = "report_type"        # Selecting report type
    REPORT_DATE = "report_date"        # Selecting report date
    ADMIN_WAITING = "admin_waiting"    # Waiting for admin text input
    RESULT_DATE = "result_date"        # Selecting result date
    RESULT_REGION = "result_region"    # Selecting result region
    ADMIN_MENU = "admin_menu"          # Admin top-level menu

VALID_STATES = {
    UserState.IDLE,
    UserState.BET_REGION,
    UserState.BET_INPUT,
    UserState.ODI_DATE,
    UserState.REPORT_TYPE,
    UserState.REPORT_DATE,
    UserState.ADMIN_WAITING,
    UserState.RESULT_DATE,
    UserState.RESULT_REGION,
    UserState.ADMIN_MENU,
}

# State → keyboard builder mapping (used for consistent back/menu transitions)
STATE_KEYBOARD_BUILDERS: dict[str, callable] = {}
VALID_REGIONS = {"MN", "MT", "MB"}
MENU_BUTTONS_LIST = ["Bet", "Report", "Result", "Other Day Input", "Admin", "Info"]

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")
DEFAULT_ADMIN_USER_IDS = os.getenv("DEFAULT_ADMIN_USER_IDS", "")
VERSION_FILE = Path("VERSION.txt")

MENU_BUTTONS = MENU_BUTTONS_LIST  # backward compat alias

CALLBACK_ODI_MENU = "odi_menu"
CALLBACK_ODI_DATE_PREFIX = "odi_date:"
CALLBACK_ODI_SET_CUSTOM = "odi_set_custom"
CALLBACK_ODI_SET_TODAY = "odi_set_today"
CALLBACK_ODI_CLOSE = "odi_close"

CALLBACK_ADMIN_MENU = "admin_menu"
CALLBACK_ADMIN_SET_ADMIN = "admin_set_admin"
CALLBACK_ADMIN_VIEW_ADMINS = "admin_view_admins"
CALLBACK_ADMIN_ADD_ADMIN = "admin_add_admin"
CALLBACK_ADMIN_REMOVE_ADMIN = "admin_remove_admin"
CALLBACK_ADMIN_BACK = "admin_back"
CALLBACK_ADMIN_CLOSE = "admin_close"

CALLBACK_ADMIN_AGENT_MENU = "admin_agent_menu"
CALLBACK_ADMIN_AGENT_VIEW = "admin_agent_view"
CALLBACK_ADMIN_AGENT_EDIT = "admin_agent_edit"

CALLBACK_ADMIN_BONUS_MENU = "admin_bonus_menu"
CALLBACK_ADMIN_BONUS_VIEW = "admin_bonus_view"
CALLBACK_ADMIN_BONUS_EDIT = "admin_bonus_edit"

CALLBACK_ADMIN_LIMIT_MENU = "admin_limit_menu"
CALLBACK_ADMIN_LIMIT_VIEW = "admin_limit_view"
CALLBACK_ADMIN_LIMIT_EDIT = "admin_limit_edit"
CALLBACK_ADMIN_LIMIT_ACTION_MENU = "admin_limit_action_menu"
CALLBACK_ADMIN_LIMIT_ACTION_ACCEPT = "admin_limit_action_accept"
CALLBACK_ADMIN_LIMIT_ACTION_REJECT = "admin_limit_action_reject"
CALLBACK_ADMIN_NOTIFICATIONS_MENU = "admin_notifications_menu"
CALLBACK_ADMIN_NOTIFICATIONS_VIEW = "admin_notifications_view"
CALLBACK_ADMIN_NOTIFICATIONS_ON = "admin_notifications_on"
CALLBACK_ADMIN_NOTIFICATIONS_OFF = "admin_notifications_off"
CALLBACK_ADMIN_TIME_LIMIT_MENU = "admin_time_limit_menu"
CALLBACK_ADMIN_TIME_LIMIT_VIEW = "admin_time_limit_view"
CALLBACK_ADMIN_TIME_LIMIT_EDIT = "admin_time_limit_edit"
CALLBACK_ADMIN_SYSTEM_TZ_MENU = "admin_system_tz_menu"
CALLBACK_ADMIN_SYSTEM_TZ_VIEW = "admin_system_tz_view"
CALLBACK_ADMIN_SYSTEM_TZ_KL = "admin_system_tz_kl"
CALLBACK_ADMIN_SYSTEM_TZ_HCM = "admin_system_tz_hcm"

user_context = {}
user_last_menu_message = {}


async def _delete_last_menu_message(context: ContextTypes.DEFAULT_TYPE, chat_id: int, user_id: int) -> None:
    last_message_id = user_last_menu_message.get(user_id)
    if not last_message_id:
        return
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=last_message_id)
    except Exception:
        pass
    finally:
        user_last_menu_message.pop(user_id, None)


async def _send_menu_message(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, reply_markup) -> None:
    if not update.message or not update.effective_user or not update.effective_chat:
        return
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    await _delete_last_menu_message(context, chat_id, user_id)
    sent = await update.message.reply_text(text, reply_markup=reply_markup)
    user_last_menu_message[user_id] = sent.message_id


async def _clear_menu_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_user or not update.effective_chat:
        return
    await _delete_last_menu_message(context, update.effective_chat.id, update.effective_user.id)


result_query_service = ResultQueryService()
result_fetch_service = ResultFetchService()

transaction_report_service = TransactionReportService()
number_detail_report_service = NumberDetailReportService()
settlement_report_service = SettlementReportService()
over_limit_report_service = OverLimitReportService()

admin_auth_service = AdminAuthService(default_admin_ids_str=DEFAULT_ADMIN_USER_IDS)
admin_settings_service = AdminSettingsService()
agent_customer_repository = AgentCustomerRepository()


def log_step(message: str) -> None:
    print(message, flush=True)

# =========================================================
# Phase 1.1: ReplyKeyboard Builders
# =========================================================
def _build_main_menu_kb() -> ReplyKeyboardMarkup:
    """Reusable ReplyKeyboard for main menu state (IDLE)."""
    return ReplyKeyboardMarkup(
        [[KeyboardButton("Bet"), KeyboardButton("Report"), KeyboardButton("Result")],
         [KeyboardButton("Other Day Input"), KeyboardButton("Admin"), KeyboardButton("Info")]],
        resize_keyboard=True,
    )

def _build_region_kb() -> ReplyKeyboardMarkup:
    """ReplyKeyboard for region selection state (BET_REGION)."""
    return ReplyKeyboardMarkup(
        [[KeyboardButton("MN"), KeyboardButton("MT"), KeyboardButton("MB")],
         [KeyboardButton("⬅ Back")]],
        resize_keyboard=True,
    )

def _build_odi_kb() -> ReplyKeyboardMarkup:
    """ReplyKeyboard for Other Day Input date selection (ODI_DATE)."""
    today = date.today()
    prev_dates = [today - timedelta(days=i) for i in range(3, 0, -1)]
    next_dates = [today + timedelta(days=i) for i in range(1, 4)]
    row_prev = [KeyboardButton(d.strftime("%d/%m")) for d in prev_dates]
    row_today = [KeyboardButton(f"Today {today.strftime('%d/%m')}")]
    row_next = [KeyboardButton(d.strftime("%d/%m")) for d in next_dates]
    return ReplyKeyboardMarkup(
        [row_prev, row_today, row_next, [KeyboardButton("Set Custom Date"), KeyboardButton("⬅ Back")]],
        resize_keyboard=True,
    )

# =========================================================
# Phase 1.1: User Context Schema & State Helpers
# =========================================================
# Schema per user_id:
# {
#   "state": UserState value (default IDLE),
#   "target_date": ISO date string (default today),
#   "region": "MN"|"MT"|MB"|None,
#   "waiting_custom_date": bool (legacy, kept for backward compat),
#   "admin_waiting_action": str|None (legacy, kept for backward compat),
# }
# Cleanup rules:
#   - Transition to IDLE clears region, waiting_custom_date, admin_waiting_action
#   - Transition to BET_REGION clears region
#   - state always validated against VALID_STATES

def _ensure_user_context(user_id: int) -> None:
    if user_id not in user_context:
        user_context[user_id] = {
            "state": UserState.IDLE,
            "target_date": _today_iso(),
            "region": None,
            "waiting_custom_date": False,
            "admin_waiting_action": None,
        }
    # Ensure state key exists (migration from old format)
    if "state" not in user_context[user_id]:
        user_context[user_id]["state"] = UserState.IDLE

def _get_user_state(user_id: int) -> str:
    _ensure_user_context(user_id)
    return user_context[user_id].get("state", UserState.IDLE)

def _set_user_state(user_id: int, new_state: str) -> None:
    _ensure_user_context(user_id)
    if new_state not in VALID_STATES:
        new_state = UserState.IDLE
    user_context[user_id]["state"] = new_state
    # Cleanup on state transition
    if new_state == UserState.IDLE:
        user_context[user_id]["region"] = None
        user_context[user_id]["waiting_custom_date"] = False
        user_context[user_id]["admin_waiting_action"] = None
        user_context[user_id]["result_draw_date"] = None
        user_context[user_id]["result_region"] = None
    elif new_state == UserState.BET_REGION:
        user_context[user_id]["region"] = None
    elif new_state == UserState.RESULT_DATE:
        user_context[user_id]["result_draw_date"] = None
        user_context[user_id]["result_region"] = None
    elif new_state == UserState.ADMIN_MENU:
        # Keep admin_waiting_action for text input flow
        pass


def validate_environment() -> None:
    log_step("⚙ Loading .env ...")
    if os.path.exists(".env"):
        log_step("✅ .env file detected")
    else:
        log_step("⚠ .env file not found, continuing with system environment variables")

    log_step("🔐 Checking BOT_TOKEN ...")
    if not BOT_TOKEN:
        log_step("❌ BOT_TOKEN is missing")
        raise RuntimeError("BOT_TOKEN is missing in .env or environment variables")
    log_step("✅ BOT_TOKEN loaded")

    if ADMIN_CHAT_ID:
        log_step(f"✅ ADMIN_CHAT_ID loaded: {ADMIN_CHAT_ID}")
    else:
        log_step("⚠ ADMIN_CHAT_ID not set, startup Telegram notification will be skipped")

    if DEFAULT_ADMIN_USER_IDS:
        log_step(f"✅ DEFAULT_ADMIN_USER_IDS loaded: {DEFAULT_ADMIN_USER_IDS}")
    else:
        log_step("⚠ DEFAULT_ADMIN_USER_IDS not set")


def initialize_database() -> None:
    log_step("🗄 Initializing database ...")
    init_database()
    admin_auth_service.init_and_sync()
    admin_settings_service.init_and_sync()
    agent_customer_repository.init_table()
    log_step("✅ Database ready")


async def post_init(application: Application) -> None:
    log_step("🤖 Handlers ready")
    log_step(f"🚀 M33 Lotto Bot started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if not ADMIN_CHAT_ID:
        return

    try:
        await application.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=(
                "🚀 M33 Lotto Bot 已上线\n"
                f"🕒 Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                "✅ Status: Running"
            ),
        )
        log_step("✅ Startup notification sent to admin")
    except Exception as e:
        log_step(f"⚠ Failed to send startup notification to admin: {e}")


# =========================================================
# Environment helpers
# =========================================================
def _today_iso() -> str:
    return date.today().isoformat()


def _get_user_env(user_id: int) -> dict:
    _ensure_user_context(user_id)
    return user_context[user_id]


def _get_user_target_date(user_id: int) -> str:
    return _get_user_env(user_id)["target_date"]


def _get_user_region(user_id: int) -> str | None:
    return _get_user_env(user_id)["region"]


def _set_user_region(user_id: int, region: str | None) -> None:
    _ensure_user_context(user_id)
    user_context[user_id]["region"] = region.upper() if region else None


def _set_user_target_date(user_id: int, target_date: str) -> None:
    _ensure_user_context(user_id)
    user_context[user_id]["target_date"] = target_date
    user_context[user_id]["region"] = None
    user_context[user_id]["waiting_custom_date"] = False


def _set_waiting_custom_date(user_id: int, waiting: bool) -> None:
    _ensure_user_context(user_id)
    user_context[user_id]["waiting_custom_date"] = waiting


def _is_waiting_custom_date(user_id: int) -> bool:
    return bool(_get_user_env(user_id).get("waiting_custom_date"))


def _set_admin_waiting_action(user_id: int, action: str | None) -> None:
    _ensure_user_context(user_id)
    user_context[user_id]["admin_waiting_action"] = action


def _get_admin_waiting_action(user_id: int) -> str | None:
    _ensure_user_context(user_id)
    return user_context[user_id].get("admin_waiting_action")


def _parse_custom_date_or_none(text: str) -> str | None:
    try:
        parsed = datetime.strptime(text.strip(), "%Y-%m-%d").date()
        return parsed.isoformat()
    except ValueError:
        return None


def _build_env_region_message(user_id: int, region: str) -> str:
    target_date = _get_user_target_date(user_id)
    base = f"You are now in {region} bet mode.\nDate: {target_date}"

    try:
        target_date_obj = datetime.strptime(target_date, "%Y-%m-%d").date()
        allowed_regions = get_allowed_regions(target_date_obj, region)
    except Exception:
        allowed_regions = []

    region = str(region).upper()
    if region in {"MN", "MT"} and allowed_regions:
        region_codes = ", ".join(code.upper() for code in allowed_regions)
        if target_date == _today_iso():
            return f"{base} (Today)\n({region_codes})"
        return f"{base}\n({region_codes})"

    if target_date == _today_iso():
        return f"{base} (Today)"
    return base


def _get_user_result_draw_date(user_id: int) -> str | None:
    return _get_user_env(user_id).get("result_draw_date")


def _set_user_result_draw_date(user_id: int, draw_date: str) -> None:
    _ensure_user_context(user_id)
    user_context[user_id]["result_draw_date"] = draw_date


def _get_user_result_region(user_id: int) -> str | None:
    return _get_user_env(user_id).get("result_region")


def _set_user_result_region(user_id: int, region: str | None) -> None:
    _ensure_user_context(user_id)
    user_context[user_id]["result_region"] = region.upper() if region else None


def _build_delete_success_message(response_text: str) -> str:
    return response_text


def _menu_anchor_text() -> str:
    return "ㅤ"


def _get_app_version() -> str:
    try:
        if VERSION_FILE.exists():
            return VERSION_FILE.read_text(encoding="utf-8").strip() or "unknown"
    except Exception:
        pass
    return "unknown"


def _build_info_text() -> str:
    version = _get_app_version()
    return "\n".join(
        [
            "INFO",
            "",
            "REGION CODE",
            "",
            "MN",
            "--------------------------",
            "Tg   = tien giang",
            "Kg   = kien giang",
            "Dl   = da lat",
            "Tp   = hcm",
            "Dt   = dong thap",
            "Cm   = ca mau",
            "Vt   = vung tau",
            "Bt   = ben tre",
            "Bl   = bac lieu",
            "Dn   = dong nai",
            "Ct   = can tho",
            "St   = soc trang",
            "Tn   = tay ninh",
            "Ag   = an giang",
            "Bth  = binh thuan",
            "Bd   = binh duong",
            "Vl   = vinh long",
            "Tv   = tra vinh",
            "La   = long an",
            "Bp   = binh phuoc",
            "Hg   = hau giang",
            "",
            "MT",
            "--------------------------",
            "Tth  = hue",
            "Py   = phu yen",
            "Dla  = dac lac",
            "Qna  = Duang nam",
            "Dna  = da nang",
            "Kh   = khanh hoa",
            "Bdi  = Kinh dinh",
            "Qtr  = quang tri",
            "Qbi  = quang binh",
            "Gl   = gia lai",
            "Nth  = ninh thuan",
            "Qng  = quang ngai",
            "Dno  = dak nong",
            "Kt   = kon tum",
            "",
            "MB",
            "--------------------------",
            "",
            "FOR FURTHER INFORMATION",
            "Telegram: @M33_VN",
            f"Version : {version}",
        ]
    )


def _as_monospace_html(text: str) -> str:
    return f"<pre>{escape(str(text))}</pre>"


def _build_report_type_kb() -> ReplyKeyboardMarkup:
    """ReplyKeyboard for report type selection (REPORT_TYPE)."""
    return ReplyKeyboardMarkup(
        [[KeyboardButton(REPORT_LABEL_TRANSACTION), KeyboardButton(REPORT_LABEL_SETTLEMENT)],
         [KeyboardButton(REPORT_LABEL_NUMBER_DETAIL), KeyboardButton(REPORT_LABEL_OVER_LIMIT)],
         [KeyboardButton("⬅ Back")]],
        resize_keyboard=True,
    )

def _build_report_date_kb() -> ReplyKeyboardMarkup:
    """ReplyKeyboard for report date selection (REPORT_DATE)."""
    today = date.today()
    dates = [today - timedelta(days=i) for i in range(7)]
    row1 = [KeyboardButton(f"Today {dates[0].strftime('%d/%m')}")]
    row2 = [KeyboardButton(d.strftime("%d/%m")) for d in dates[1:3]]
    row3 = [KeyboardButton(d.strftime("%d/%m")) for d in dates[3:5]]
    row4 = [KeyboardButton(d.strftime("%d/%m")) for d in dates[5:7]]
    return ReplyKeyboardMarkup(
        [row1, row2, row3, row4, [KeyboardButton("⬅ Back")]],
        resize_keyboard=True,
    )

# =========================================================
# Report helpers
# =========================================================
def _build_report_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(REPORT_LABEL_TRANSACTION, callback_data=f"{REPORT_CALLBACK_TYPE_PREFIX}{REPORT_TYPE_TRANSACTION}"),
            InlineKeyboardButton(REPORT_LABEL_SETTLEMENT, callback_data=f"{REPORT_CALLBACK_TYPE_PREFIX}{REPORT_TYPE_SETTLEMENT}"),
        ],
        [
            InlineKeyboardButton(REPORT_LABEL_NUMBER_DETAIL, callback_data=f"{REPORT_CALLBACK_TYPE_PREFIX}{REPORT_TYPE_NUMBER_DETAIL}"),
            InlineKeyboardButton(REPORT_LABEL_OVER_LIMIT, callback_data=f"{REPORT_CALLBACK_TYPE_PREFIX}{REPORT_TYPE_OVER_LIMIT}"),
        ],
        [InlineKeyboardButton("❌ Close", callback_data=REPORT_CALLBACK_CLOSE)],
    ]
    return InlineKeyboardMarkup(keyboard)


def _build_report_date_text(report_type: str) -> str:
    label_map = {
        REPORT_TYPE_TRANSACTION: REPORT_LABEL_TRANSACTION,
        REPORT_TYPE_SETTLEMENT: REPORT_LABEL_SETTLEMENT,
        REPORT_TYPE_NUMBER_DETAIL: REPORT_LABEL_NUMBER_DETAIL,
        REPORT_TYPE_OVER_LIMIT: REPORT_LABEL_OVER_LIMIT,
    }
    return label_map.get(report_type, "Report")


def _build_report_date_keyboard(report_type: str) -> InlineKeyboardMarkup:
    today = date.today()
    dates = [today - timedelta(days=i) for i in range(7)]
    keyboard: list[list[InlineKeyboardButton]] = []

    first = dates[0]
    keyboard.append([
        InlineKeyboardButton(
            f"Today {first.strftime('%d/%m')}",
            callback_data=f"{REPORT_CALLBACK_DATE_PREFIX}{report_type}:{first.isoformat()}",
        )
    ])

    row: list[InlineKeyboardButton] = []
    for d in dates[1:]:
        row.append(
            InlineKeyboardButton(
                d.strftime("%d/%m"),
                callback_data=f"{REPORT_CALLBACK_DATE_PREFIX}{report_type}:{d.isoformat()}",
            )
        )
        if len(row) == 2:
            keyboard.append(row)
            row = []

    if row:
        keyboard.append(row)

    keyboard.append([InlineKeyboardButton("⬅ Back", callback_data=REPORT_CALLBACK_BACK_TO_MENU)])
    return InlineKeyboardMarkup(keyboard)


def _build_report_action_keyboard(report_type: str, target_date: str) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("📄 Export HTML", callback_data=f"{REPORT_CALLBACK_EXPORT_PREFIX}{report_type}:{target_date}")],
        [InlineKeyboardButton("📅 Change Date", callback_data=f"{REPORT_CALLBACK_TYPE_PREFIX}{report_type}")],
        [InlineKeyboardButton("⬅ Back", callback_data=REPORT_CALLBACK_BACK_TO_MENU)],
    ]
    return InlineKeyboardMarkup(keyboard)


def _build_coming_soon_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅ Back", callback_data=REPORT_CALLBACK_BACK_TO_MENU)]])


def _report_filename(report_type: str, target_date: str) -> str:
    if report_type == REPORT_TYPE_TRANSACTION:
        return f"transaction_report_{target_date}.html"
    if report_type == REPORT_TYPE_NUMBER_DETAIL:
        return f"number_detail_report_{target_date}.html"
    if report_type == REPORT_TYPE_SETTLEMENT:
        return f"settlement_report_{target_date}.html"
    if report_type == REPORT_TYPE_OVER_LIMIT:
        return f"over_limit_report_{target_date}.html"
    return f"report_{report_type}_{target_date}.html"


def _generate_report_text(report_type: str, target_date: str) -> str | None:
    """Generate report text for a given type and date. Returns None for unknown types."""
    if report_type == REPORT_TYPE_TRANSACTION:
        report_data = transaction_report_service.generate_report(target_date)
        return format_transaction_report(report_data)
    if report_type == REPORT_TYPE_NUMBER_DETAIL:
        report_data = number_detail_report_service.generate_report(target_date)
        return format_number_detail_report(report_data)
    if report_type == REPORT_TYPE_SETTLEMENT:
        current_rate = ReportNormalizer.to_decimal(admin_settings_service.get_agent_commission_rate())
        report_data = settlement_report_service.generate_report(target_date=target_date, agent_commission_rate=current_rate)
        return format_settlement_report_telegram(report_data)
    if report_type == REPORT_TYPE_OVER_LIMIT:
        report_data = over_limit_report_service.generate(target_date)
        return format_over_limit_report(report_data)
    return None

# =========================================================
# Admin helpers
# =========================================================
def _build_admin_menu_text() -> str:
    return "Admin"


def _build_admin_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("1. Agent Comm Setting", callback_data=CALLBACK_ADMIN_AGENT_MENU)],
        [InlineKeyboardButton("2. Bonus Payout Setting", callback_data=CALLBACK_ADMIN_BONUS_MENU)],
        [InlineKeyboardButton("3. Over Limit Setting", callback_data=CALLBACK_ADMIN_LIMIT_MENU)],
        [InlineKeyboardButton("4. Notifications", callback_data=CALLBACK_ADMIN_NOTIFICATIONS_MENU)],
        [InlineKeyboardButton("5. Bet Time Limit", callback_data=CALLBACK_ADMIN_TIME_LIMIT_MENU)],
        [InlineKeyboardButton("6. System Time Zone", callback_data=CALLBACK_ADMIN_SYSTEM_TZ_MENU)],
        [InlineKeyboardButton("7. Set Admin", callback_data=CALLBACK_ADMIN_SET_ADMIN)],
        [InlineKeyboardButton("❌ Close", callback_data=CALLBACK_ADMIN_CLOSE)],
    ]
    return InlineKeyboardMarkup(keyboard)


def _build_admin_menu_kb() -> ReplyKeyboardMarkup:
    """ReplyKeyboard for admin menu (top-level)."""
    return ReplyKeyboardMarkup(
        [[KeyboardButton("1. Agent Comm Setting"), KeyboardButton("2. Bonus Payout Setting")],
         [KeyboardButton("3. Over Limit Setting"), KeyboardButton("4. Notifications")],
         [KeyboardButton("5. Bet Time Limit"), KeyboardButton("6. System Time Zone")],
         [KeyboardButton("7. Set Admin"), KeyboardButton("⬅ Back")]],
        resize_keyboard=True,
    )


def _build_set_admin_text() -> str:
    return "👑 Set Admin\n\nPlease choose an action:"


def _build_set_admin_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("View Admin List", callback_data=CALLBACK_ADMIN_VIEW_ADMINS)],
        [InlineKeyboardButton("Add Admin", callback_data=CALLBACK_ADMIN_ADD_ADMIN)],
        [InlineKeyboardButton("Remove Admin", callback_data=CALLBACK_ADMIN_REMOVE_ADMIN)],
        [InlineKeyboardButton("⬅ Back", callback_data=CALLBACK_ADMIN_BACK)],
    ]
    return InlineKeyboardMarkup(keyboard)


def _build_agent_comm_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("View Current Agent Comm", callback_data=CALLBACK_ADMIN_AGENT_VIEW)],
        [InlineKeyboardButton("Edit Agent Comm", callback_data=CALLBACK_ADMIN_AGENT_EDIT)],
        [InlineKeyboardButton("⬅ Back", callback_data=CALLBACK_ADMIN_BACK)],
    ]
    return InlineKeyboardMarkup(keyboard)


def _build_bonus_payout_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("View Current Bonus Payout", callback_data=CALLBACK_ADMIN_BONUS_VIEW)],
        [InlineKeyboardButton("Edit Bonus Payout", callback_data=CALLBACK_ADMIN_BONUS_EDIT)],
        [InlineKeyboardButton("⬅ Back", callback_data=CALLBACK_ADMIN_BACK)],
    ]
    return InlineKeyboardMarkup(keyboard)


def _build_over_limit_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("View Current Over Limit", callback_data=CALLBACK_ADMIN_LIMIT_VIEW)],
        [InlineKeyboardButton("Edit Over Limit", callback_data=CALLBACK_ADMIN_LIMIT_EDIT)],
        [InlineKeyboardButton("Set Over Limit Action", callback_data=CALLBACK_ADMIN_LIMIT_ACTION_MENU)],
        [InlineKeyboardButton("⬅ Back", callback_data=CALLBACK_ADMIN_BACK)],
    ]
    return InlineKeyboardMarkup(keyboard)


def _build_over_limit_action_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("Continue Accepting", callback_data=CALLBACK_ADMIN_LIMIT_ACTION_ACCEPT)],
        [InlineKeyboardButton("Reject Bet", callback_data=CALLBACK_ADMIN_LIMIT_ACTION_REJECT)],
        [InlineKeyboardButton("⬅ Back", callback_data=CALLBACK_ADMIN_LIMIT_MENU)],
    ]
    return InlineKeyboardMarkup(keyboard)


def _build_notifications_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("View Current Notification Settings", callback_data=CALLBACK_ADMIN_NOTIFICATIONS_VIEW)],
        [
            InlineKeyboardButton("ON", callback_data=CALLBACK_ADMIN_NOTIFICATIONS_ON),
            InlineKeyboardButton("OFF", callback_data=CALLBACK_ADMIN_NOTIFICATIONS_OFF),
        ],
        [InlineKeyboardButton("⬅ Back", callback_data=CALLBACK_ADMIN_BACK)],
    ]
    return InlineKeyboardMarkup(keyboard)


def _build_time_limit_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("View Current Cutoff Time", callback_data=CALLBACK_ADMIN_TIME_LIMIT_VIEW)],
        [InlineKeyboardButton("Edit Cutoff Time", callback_data=CALLBACK_ADMIN_TIME_LIMIT_EDIT)],
        [InlineKeyboardButton("⬅ Back", callback_data=CALLBACK_ADMIN_BACK)],
    ]
    return InlineKeyboardMarkup(keyboard)


def _build_system_timezone_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("View Current Time Zone", callback_data=CALLBACK_ADMIN_SYSTEM_TZ_VIEW)],
        [
            InlineKeyboardButton("Kuala Lumpur", callback_data=CALLBACK_ADMIN_SYSTEM_TZ_KL),
            InlineKeyboardButton("Ho Chi Minh", callback_data=CALLBACK_ADMIN_SYSTEM_TZ_HCM),
        ],
        [InlineKeyboardButton("⬅ Back", callback_data=CALLBACK_ADMIN_BACK)],
    ]
    return InlineKeyboardMarkup(keyboard)


def _format_admin_list_text() -> str:
    admins = admin_auth_service.list_admins()
    if not admins:
        return "👑 Admin List\n\nNo admin found."
    lines = ["👑 Admin List", ""]
    for idx, item in enumerate(admins, start=1):
        user_id = item["user_id"]
        username = item.get("username") or "-"
        suffix = " (default)" if item.get("is_default") else ""
        lines.append(f"{idx}. {user_id}{suffix}")
        lines.append(f"   username: {username}")
        lines.append("")
    return "\n".join(lines).strip()


async def settlement_today_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    target_date = _today_iso()
    current_rate = ReportNormalizer.to_decimal(admin_settings_service.get_agent_commission_rate())
    report_data = settlement_report_service.generate_report(
        target_date=target_date,
        agent_commission_rate=current_rate,
    )
    text = format_settlement_report_telegram(report_data)
    await _clear_menu_message(update, context)
    await update.message.reply_text(_as_monospace_html(text), parse_mode="HTML", reply_markup=ReplyKeyboardRemove())


# =========================================================
# Commands
# =========================================================
async def mn_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.effective_user:
        return
    user_id = update.effective_user.id
    _set_user_target_date(user_id, _today_iso())
    _set_user_region(user_id, "MN")
    await _clear_menu_message(update, context)
    await update.message.reply_text(_build_env_region_message(user_id, "MN"), reply_markup=ReplyKeyboardRemove())


async def mt_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.effective_user:
        return
    user_id = update.effective_user.id
    _set_user_target_date(user_id, _today_iso())
    _set_user_region(user_id, "MT")
    await _clear_menu_message(update, context)
    await update.message.reply_text(_build_env_region_message(user_id, "MT"), reply_markup=ReplyKeyboardRemove())


async def mb_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.effective_user:
        return
    user_id = update.effective_user.id
    _set_user_target_date(user_id, _today_iso())
    _set_user_region(user_id, "MB")
    await _clear_menu_message(update, context)
    await update.message.reply_text(_build_env_region_message(user_id, "MB"), reply_markup=ReplyKeyboardRemove())


async def myid_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.effective_user:
        return
    await _clear_menu_message(update, context)
    await update.message.reply_text(f"Your Telegram user_id: {update.effective_user.id}", reply_markup=ReplyKeyboardRemove())


async def delete_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.effective_user:
        return
    user_id = update.effective_user.id
    args = context.args or []
    if len(args) < 1:
        await update.message.reply_text("❌ Usage: /delete N1")
        return
    ticket_no = str(args[0]).upper()
    target_date = _get_user_target_date(user_id)
    _, response_text = delete_ticket(ticket_no, target_date)
    await _clear_menu_message(update, context)
    await update.message.reply_text(_as_monospace_html(_build_delete_success_message(response_text)), parse_mode="HTML", reply_markup=ReplyKeyboardRemove())


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.effective_user:
        return
    user_id = update.effective_user.id
    _set_user_state(user_id, UserState.IDLE)
    await show_main_menu(update, context)


# =========================================================
# Menus
# =========================================================
async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.effective_user:
        return
    _set_user_state(update.effective_user.id, UserState.IDLE)
    await _send_menu_message(update, context, _menu_anchor_text(), _build_main_menu_kb())


async def show_bet_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return
    reply_markup = get_bet_menu_keyboard()
    await _send_menu_message(update, context, "Bet", reply_markup)


async def main_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # 清理用户状态，确保没有旧信息遗留
    user_id = update.effective_user.id
    _set_user_state(user_id, UserState.IDLE)
    if not update.message or not update.effective_user:
        return
    text = update.message.text
    user_id = update.effective_user.id
    _ensure_user_context(user_id)

    if text == "Bet":
        _set_user_state(user_id, UserState.BET_REGION)
        _set_user_target_date(user_id, _today_iso())
        await _send_menu_message(update, context, "Select region:", _build_region_kb())
    elif text == "Report":
        _set_user_state(user_id, UserState.REPORT_TYPE)
        await _send_menu_message(update, context, "Select report type:", _build_report_type_kb())
    elif text == "Result":
        _set_user_state(user_id, UserState.RESULT_DATE)
        await _send_menu_message(update, context, _build_result_menu_text(), _build_result_date_kb())
    elif text == "Other Day Input":
        _set_user_state(user_id, UserState.ODI_DATE)
        await _send_menu_message(update, context, "Select date:", _build_odi_kb())
    elif text == "Admin":
        if not admin_auth_service.is_admin(user_id):
            await update.message.reply_text("您没有权限访问此功能。")
            return
        _set_user_state(user_id, UserState.ADMIN_MENU)
        await _send_menu_message(update, context, _build_admin_menu_text(), _build_admin_menu_kb())
    elif text == "Info":
        await _clear_menu_message(update, context)
        await update.message.reply_text(_as_monospace_html(_build_info_text()), parse_mode="HTML", reply_markup=ReplyKeyboardRemove())
    else:
        await show_main_menu(update, context)


async def region_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.effective_user:
        return
    user_id = update.effective_user.id
    region = (update.message.text or "").strip().upper()
    _ensure_user_context(user_id)
    if region in VALID_REGIONS:
        _set_user_state(user_id, UserState.BET_INPUT)
        _set_user_region(user_id, region)
        await _clear_menu_message(update, context)
        await update.message.reply_text(_build_env_region_message(user_id, region), reply_markup=ReplyKeyboardRemove())
    else:
        await update.message.reply_text("Invalid region. Please select MN, MT, or MB.")


# =========================================================
# Report UI
# =========================================================
async def handle_report_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query:
        return
    await query.answer()
    await query.edit_message_text(text=REPORT_MENU_TITLE, reply_markup=_build_report_menu_keyboard())


async def handle_report_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query:
        return
    await query.answer()
    report_type = query.data.replace(REPORT_CALLBACK_TYPE_PREFIX, "", 1)
    await query.edit_message_text(text=_build_report_date_text(report_type), reply_markup=_build_report_date_keyboard(report_type))


async def handle_report_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query:
        return
    await query.answer()
    payload = query.data.replace(REPORT_CALLBACK_DATE_PREFIX, "", 1)
    try:
        report_type, target_date = payload.split(":")
    except ValueError:
        await query.edit_message_text("Invalid report request.")
        return

    if report_type == REPORT_TYPE_TRANSACTION:
        report_data = transaction_report_service.generate_report(target_date)
        text = format_transaction_report(report_data)
    elif report_type == REPORT_TYPE_NUMBER_DETAIL:
        report_data = number_detail_report_service.generate_report(target_date)
        text = format_number_detail_report(report_data)
    elif report_type == REPORT_TYPE_SETTLEMENT:
        current_rate = ReportNormalizer.to_decimal(admin_settings_service.get_agent_commission_rate())
        report_data = settlement_report_service.generate_report(target_date=target_date, agent_commission_rate=current_rate)
        text = format_settlement_report_telegram(report_data)
    elif report_type == REPORT_TYPE_OVER_LIMIT:
        report_data = over_limit_report_service.generate(target_date)
        text = format_over_limit_report(report_data)
    else:
        await query.edit_message_text(text=REPORT_COMING_SOON_TEXT, reply_markup=_build_coming_soon_keyboard())
        return

    await query.edit_message_text(text=_as_monospace_html(text), reply_markup=_build_report_action_keyboard(report_type, target_date), parse_mode="HTML")


async def handle_report_export(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query:
        return
    await query.answer()
    payload = query.data.replace(REPORT_CALLBACK_EXPORT_PREFIX, "", 1)
    try:
        report_type, target_date = payload.split(":")
    except ValueError:
        await query.edit_message_text("Invalid export request.")
        return

    if report_type == REPORT_TYPE_TRANSACTION:
        report_data = transaction_report_service.generate_report(target_date)
        html = build_transaction_report_html(report_data)
    elif report_type == REPORT_TYPE_NUMBER_DETAIL:
        report_data = number_detail_report_service.generate_report(target_date)
        html = build_number_detail_report_html(report_data)
    elif report_type == REPORT_TYPE_SETTLEMENT:
        current_rate = ReportNormalizer.to_decimal(admin_settings_service.get_agent_commission_rate())
        report_data = settlement_report_service.generate_report(target_date=target_date, agent_commission_rate=current_rate)
        html = export_settlement_report_html(report_data)
    elif report_type == REPORT_TYPE_OVER_LIMIT:
        report_data = over_limit_report_service.generate(target_date)
        html = export_over_limit_report_html(report_data)
    else:
        await query.answer("Export not available.", show_alert=True)
        return

    filename = _report_filename(report_type, target_date)
    output_path = Path("data") / filename
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")

    if query.message:
        with output_path.open("rb") as f:
            await query.message.reply_document(document=f, filename=filename)


async def handle_report_close(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query:
        return
    await query.answer()
    try:
        if query.message:
            await query.message.delete()
    except Exception:
        try:
            await query.edit_message_text("Closed.")
        except Exception:
            pass


# =========================================================
# Admin UI
# =========================================================
async def handle_admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.from_user:
        return
    await query.answer()
    if not admin_auth_service.is_admin(query.from_user.id):
        await query.edit_message_text("您没有权限访问此功能。")
        return
    await query.edit_message_text(text=_build_admin_menu_text(), reply_markup=_build_admin_menu_keyboard())


async def handle_admin_set_admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.from_user:
        return
    await query.answer()
    if not admin_auth_service.is_admin(query.from_user.id):
        await query.edit_message_text("您没有权限访问此功能。")
        return
    await query.edit_message_text(text=_build_set_admin_text(), reply_markup=_build_set_admin_keyboard())


async def handle_admin_view_admins(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.from_user:
        return
    await query.answer()
    if not admin_auth_service.is_admin(query.from_user.id):
        await query.edit_message_text("您没有权限访问此功能。")
        return
    await query.edit_message_text(text=_format_admin_list_text(), reply_markup=_build_set_admin_keyboard())


async def handle_admin_add_admin_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.from_user:
        return
    await query.answer()
    if not admin_auth_service.is_admin(query.from_user.id):
        await query.edit_message_text("您没有权限访问此功能。")
        return
    _set_admin_waiting_action(query.from_user.id, "ADD_ADMIN")
    await query.edit_message_text(
        text="Please enter Telegram user id to add as ADMIN:",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅ Back", callback_data=CALLBACK_ADMIN_SET_ADMIN)]]),
    )


async def handle_admin_remove_admin_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.from_user:
        return
    await query.answer()
    if not admin_auth_service.is_admin(query.from_user.id):
        await query.edit_message_text("您没有权限访问此功能。")
        return
    _set_admin_waiting_action(query.from_user.id, "REMOVE_ADMIN")
    await query.edit_message_text(
        text="Please enter Telegram user id to remove from ADMIN:",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅ Back", callback_data=CALLBACK_ADMIN_SET_ADMIN)]]),
    )


async def handle_admin_agent_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.from_user:
        return
    await query.answer()
    await query.edit_message_text(text="Agent Comm Setting", reply_markup=_build_agent_comm_keyboard())


async def handle_admin_agent_view(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.from_user:
        return
    await query.answer()
    rate = admin_settings_service.get_agent_commission_rate()
    await query.edit_message_text(text=f"Agent Commission Rate\n\nCurrent: {rate}%", reply_markup=_build_agent_comm_keyboard())


async def handle_admin_agent_edit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.from_user:
        return
    await query.answer()
    _set_admin_waiting_action(query.from_user.id, "SET_AGENT_COMM")
    await query.edit_message_text(
        text="Please enter new commission rate (%):",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅ Back", callback_data=CALLBACK_ADMIN_AGENT_MENU)]]),
    )


async def handle_admin_bonus_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.from_user:
        return
    await query.answer()
    await query.edit_message_text(text="Bonus Payout Setting", reply_markup=_build_bonus_payout_keyboard())


async def handle_admin_bonus_view(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.from_user:
        return
    await query.answer()
    await query.edit_message_text(text=admin_settings_service.format_bonus_payout_text(), reply_markup=_build_bonus_payout_keyboard())


async def handle_admin_bonus_edit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.from_user:
        return
    await query.answer()
    _set_admin_waiting_action(query.from_user.id, "SET_BONUS_PAYOUT_BULK")
    template = admin_settings_service.build_bonus_edit_template()
    await query.edit_message_text(
        text=f"Please edit Bonus Payout and send back in this format:\n\n{template}",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅ Back", callback_data=CALLBACK_ADMIN_BONUS_MENU)]]),
    )


async def handle_admin_limit_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.from_user:
        return
    await query.answer()
    await query.edit_message_text(text="Over Limit Setting", reply_markup=_build_over_limit_keyboard())


async def handle_admin_limit_view(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.from_user:
        return
    await query.answer()
    await query.edit_message_text(text=admin_settings_service.format_limit_text(), reply_markup=_build_over_limit_keyboard())


async def handle_admin_limit_edit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.from_user:
        return
    await query.answer()
    _set_admin_waiting_action(query.from_user.id, "SET_OVER_LIMIT_BULK")
    template = admin_settings_service.build_limit_edit_template()
    await query.edit_message_text(
        text=f"Please edit Over Limit and send back in this format:\n\n{template}",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅ Back", callback_data=CALLBACK_ADMIN_LIMIT_MENU)]]),
    )


async def handle_admin_limit_action_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.from_user:
        return
    await query.answer()
    current_action = admin_settings_service.get_over_limit_action()
    await query.edit_message_text(text=f"Over Limit Action\n\nCurrent: {current_action}", reply_markup=_build_over_limit_action_keyboard())


async def handle_admin_limit_action_accept(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query:
        return
    await query.answer()
    admin_settings_service.set_over_limit_action("ACCEPT")
    await query.edit_message_text(text="✅ Over Limit Action set to ACCEPT", reply_markup=_build_over_limit_action_keyboard())


async def handle_admin_limit_action_reject(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query:
        return
    await query.answer()
    admin_settings_service.set_over_limit_action("REJECT")
    await query.edit_message_text(text="✅ Over Limit Action set to REJECT", reply_markup=_build_over_limit_action_keyboard())


async def handle_admin_notifications_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.from_user:
        return
    await query.answer()
    await query.edit_message_text(text="Notifications", reply_markup=_build_notifications_keyboard())


async def handle_admin_notifications_view(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.from_user:
        return
    await query.answer()
    await query.edit_message_text(text=admin_settings_service.format_notification_text(), reply_markup=_build_notifications_keyboard())


async def handle_admin_notifications_on(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.from_user:
        return
    await query.answer()
    admin_settings_service.set_customer_notification_enabled(True)
    await query.edit_message_text(text="✅ Customer Notification set to ON", reply_markup=_build_notifications_keyboard())


async def handle_admin_notifications_off(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.from_user:
        return
    await query.answer()
    admin_settings_service.set_customer_notification_enabled(False)
    await query.edit_message_text(text="✅ Customer Notification set to OFF", reply_markup=_build_notifications_keyboard())


async def handle_admin_time_limit_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.from_user:
        return
    await query.answer()
    await query.edit_message_text(text="Bet Time Limit", reply_markup=_build_time_limit_keyboard())


async def handle_admin_time_limit_view(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.from_user:
        return
    await query.answer()
    await query.edit_message_text(text=admin_settings_service.format_cutoff_time_text(), reply_markup=_build_time_limit_keyboard())


async def handle_admin_time_limit_edit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.from_user:
        return
    await query.answer()
    _set_admin_waiting_action(query.from_user.id, "SET_CUTOFF_TIME_BULK")
    template = admin_settings_service.build_cutoff_time_edit_template()
    await query.edit_message_text(
        text=f"Please edit Cutoff Time and send back in this format:\n\n{template}",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅ Back", callback_data=CALLBACK_ADMIN_TIME_LIMIT_MENU)]]),
    )


async def handle_admin_system_tz_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.from_user:
        return
    await query.answer()
    await query.edit_message_text(text="System Time Zone", reply_markup=_build_system_timezone_keyboard())


async def handle_admin_system_tz_view(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.from_user:
        return
    await query.answer()
    await query.edit_message_text(text=admin_settings_service.format_system_timezone_text(), reply_markup=_build_system_timezone_keyboard())


async def handle_admin_system_tz_kl(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.from_user:
        return
    await query.answer()
    admin_settings_service.set_system_timezone_name("Asia/Kuala_Lumpur")
    await query.edit_message_text(text="✅ System Time Zone set to Asia/Kuala_Lumpur", reply_markup=_build_system_timezone_keyboard())


async def handle_admin_system_tz_hcm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.from_user:
        return
    await query.answer()
    admin_settings_service.set_system_timezone_name("Asia/Ho_Chi_Minh")
    await query.edit_message_text(text="✅ System Time Zone set to Asia/Ho_Chi_Minh", reply_markup=_build_system_timezone_keyboard())


async def handle_admin_back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.from_user:
        return
    await query.answer()
    if not admin_auth_service.is_admin(query.from_user.id):
        await query.edit_message_text("您没有权限访问此功能。")
        return
    await query.edit_message_text(text=_build_admin_menu_text(), reply_markup=_build_admin_menu_keyboard())


async def handle_admin_close(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query:
        return
    await query.answer()
    try:
        if query.message:
            await query.message.delete()
    except Exception:
        try:
            await query.edit_message_text("Closed.")
        except Exception:
            pass


# =========================================================
# Other Day UI
# =========================================================
def _build_other_day_menu_text(user_id: int) -> str:
    return "Other Day Input"


def _build_other_day_keyboard() -> InlineKeyboardMarkup:
    today = date.today()
    prev_dates = [today - timedelta(days=i) for i in range(3, 0, -1)]
    next_dates = [today + timedelta(days=i) for i in range(1, 4)]
    keyboard = [
        [InlineKeyboardButton(d.strftime("%d/%m"), callback_data=f"{CALLBACK_ODI_DATE_PREFIX}{d.isoformat()}") for d in prev_dates],
        [InlineKeyboardButton(f"Today {today.strftime('%d/%m')}", callback_data=CALLBACK_ODI_SET_TODAY)],
        [InlineKeyboardButton(d.strftime("%d/%m"), callback_data=f"{CALLBACK_ODI_DATE_PREFIX}{d.isoformat()}") for d in next_dates],
        [InlineKeyboardButton("Set Custom Date", callback_data=CALLBACK_ODI_SET_CUSTOM)],
        [InlineKeyboardButton("❌ Close", callback_data=CALLBACK_ODI_CLOSE)],
    ]
    return InlineKeyboardMarkup(keyboard)


async def handle_other_day_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query or not query.from_user:
        return
    user_id = query.from_user.id
    _ensure_user_context(user_id)
    await query.answer()
    await query.edit_message_text(text=_build_other_day_menu_text(user_id), reply_markup=_build_other_day_keyboard())


async def handle_other_day_select_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query or not query.from_user:
        return
    user_id = query.from_user.id
    _ensure_user_context(user_id)
    await query.answer()
    target_date = query.data.replace(CALLBACK_ODI_DATE_PREFIX, "", 1)
    _set_user_target_date(user_id, target_date)
    await query.edit_message_text(text="Other Day Input")
    if query.message:
        await query.message.reply_text("Bet", reply_markup=get_bet_menu_keyboard())


async def handle_other_day_set_today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query or not query.from_user:
        return
    user_id = query.from_user.id
    _ensure_user_context(user_id)
    await query.answer()
    _set_user_target_date(user_id, _today_iso())
    await query.edit_message_text(text="Other Day Input")
    if query.message:
        await query.message.reply_text("Bet", reply_markup=get_bet_menu_keyboard())


async def handle_other_day_set_custom(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query or not query.from_user:
        return
    user_id = query.from_user.id
    _ensure_user_context(user_id)
    await query.answer()
    _set_waiting_custom_date(user_id, True)
    await query.edit_message_text(text="Custom Date\n\nYYYY-MM-DD")


async def handle_other_day_close(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        return
    await query.answer()
    try:
        if query.message:
            await query.message.delete()
    except Exception:
        try:
            await query.edit_message_text("Closed.")
        except Exception:
            pass


# =========================================================
# Result UI
# =========================================================
def _build_result_menu_text() -> str:
    return "Result"


def _build_result_region_text(draw_date: str) -> str:
    return "Result"


def _build_result_date_kb() -> ReplyKeyboardMarkup:
    """ReplyKeyboard for result date selection (RESULT_DATE)."""
    today = datetime.now().date()
    dates = [today - timedelta(days=i) for i in range(7)]
    row1 = [KeyboardButton(f"Today {dates[0].strftime('%d/%m')}")]
    row2 = [KeyboardButton(d.strftime("%d/%m")) for d in dates[1:3]]
    row3 = [KeyboardButton(d.strftime("%d/%m")) for d in dates[3:5]]
    row4 = [KeyboardButton(d.strftime("%d/%m")) for d in dates[5:7]]
    return ReplyKeyboardMarkup(
        [row1, row2, row3, row4, [KeyboardButton("⬅ Back")]],
        resize_keyboard=True,
    )


def _build_result_region_kb() -> ReplyKeyboardMarkup:
    """ReplyKeyboard for result region selection (RESULT_REGION)."""
    return ReplyKeyboardMarkup(
        [[KeyboardButton("MN"), KeyboardButton("MT"), KeyboardButton("MB")],
         [KeyboardButton("⬅ Back")]],
        resize_keyboard=True,
    )


def _build_result_date_keyboard() -> InlineKeyboardMarkup:
    today = datetime.now().date()
    dates = [today - timedelta(days=i) for i in range(7)]
    keyboard = []
    first = dates[0]
    keyboard.append([InlineKeyboardButton(f"Today {first.strftime('%d/%m')}", callback_data=f"{CALLBACK_RESULT_DATE_PREFIX}{first.isoformat()}")])
    row = []
    for d in dates[1:]:
        row.append(InlineKeyboardButton(d.strftime("%d/%m"), callback_data=f"{CALLBACK_RESULT_DATE_PREFIX}{d.isoformat()}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("⬅ Back", callback_data=CALLBACK_RESULT_CLOSE)])
    return InlineKeyboardMarkup(keyboard)


def _build_result_region_keyboard(draw_date: str) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("MN", callback_data=f"{CALLBACK_RESULT_VIEW_PREFIX}{draw_date}:MN"),
            InlineKeyboardButton("MT", callback_data=f"{CALLBACK_RESULT_VIEW_PREFIX}{draw_date}:MT"),
            InlineKeyboardButton("MB", callback_data=f"{CALLBACK_RESULT_VIEW_PREFIX}{draw_date}:MB"),
        ],
        [InlineKeyboardButton("⬅ Back", callback_data=CALLBACK_RESULT_MENU)],
    ]
    return InlineKeyboardMarkup(keyboard)


def _build_result_action_keyboard(draw_date: str, current_region: str, has_result: bool) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("🔄 Refresh", callback_data=f"{CALLBACK_RESULT_REFRESH_PREFIX}{draw_date}:{current_region}")],
        [
            InlineKeyboardButton("MN", callback_data=f"{CALLBACK_RESULT_VIEW_PREFIX}{draw_date}:MN"),
            InlineKeyboardButton("MT", callback_data=f"{CALLBACK_RESULT_VIEW_PREFIX}{draw_date}:MT"),
            InlineKeyboardButton("MB", callback_data=f"{CALLBACK_RESULT_VIEW_PREFIX}{draw_date}:MB"),
        ],
        [InlineKeyboardButton("📅 Change Date", callback_data=CALLBACK_RESULT_CHANGE_DATE)],
        [InlineKeyboardButton("❌ Close" if has_result else "⬅ Back", callback_data=CALLBACK_RESULT_CLOSE if has_result else CALLBACK_RESULT_MENU)],
    ]
    return InlineKeyboardMarkup(keyboard)


async def handle_result_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        return
    await query.answer()
    await query.edit_message_text(text=_build_result_menu_text(), reply_markup=_build_result_date_keyboard())


async def handle_result_date_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        return
    await query.answer()
    draw_date = query.data.replace(CALLBACK_RESULT_DATE_PREFIX, "", 1)
    await query.edit_message_text(text=_build_result_region_text(draw_date), reply_markup=_build_result_region_keyboard(draw_date))


async def handle_result_view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        return
    await query.answer()
    payload = query.data.replace(CALLBACK_RESULT_VIEW_PREFIX, "", 1)
    try:
        draw_date, region_code = payload.split(":")
    except ValueError:
        await query.edit_message_text("Invalid result request.")
        return

    result_data = result_query_service.get_or_fetch(draw_date, region_code)
    meta = result_data.get("meta")
    items = result_data.get("items", [])
    message_text = format_result_message(meta, items)
    has_result = bool(meta and meta.get("status") == "available" and items)
    await query.edit_message_text(text=_as_monospace_html(message_text), reply_markup=_build_result_action_keyboard(draw_date, region_code, has_result), parse_mode="HTML")


async def handle_result_refresh(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        return
    await query.answer()
    payload = query.data.replace(CALLBACK_RESULT_REFRESH_PREFIX, "", 1)
    try:
        draw_date, region_code = payload.split(":")
    except ValueError:
        await query.edit_message_text("Invalid refresh request.")
        return
    result_fetch_service.fetch_and_store(draw_date, region_code)
    result_data = result_query_service.get_or_fetch(draw_date, region_code)
    meta = result_data.get("meta")
    items = result_data.get("items", [])
    message_text = format_result_message(meta, items)
    has_result = bool(meta and meta.get("status") == "available" and items)
    await query.edit_message_text(text=_as_monospace_html(message_text), reply_markup=_build_result_action_keyboard(draw_date, region_code, has_result), parse_mode="HTML")


async def handle_result_change_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        return
    await query.answer()
    await query.edit_message_text(text=_build_result_menu_text(), reply_markup=_build_result_date_keyboard())


async def handle_result_close(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        return
    await query.answer()
    try:
        if query.message:
            await query.message.delete()
    except Exception:
        try:
            await query.edit_message_text("Closed.")
        except Exception:
            pass


async def result_entry_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    await update.message.reply_text(text=_build_result_menu_text(), reply_markup=_build_result_date_keyboard())


# =========================================================
# Router
# =========================================================
async def text_router(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.effective_user:
        return

    user_id = update.effective_user.id
    text = (update.message.text or "").strip()
    _ensure_user_context(user_id)
    state = _get_user_state(user_id)

    # ── State: BET_REGION (Phase 1.1 reply-keyboard region picker) ──
    if state == UserState.BET_REGION:
        region = text.upper()
        if region in VALID_REGIONS:
            _set_user_state(user_id, UserState.BET_INPUT)
            _set_user_region(user_id, region)
            await _clear_menu_message(update, context)
            await update.message.reply_text(_build_env_region_message(user_id, region), reply_markup=ReplyKeyboardRemove())
            return
        if text == "⬅ Back":
            _set_user_state(user_id, UserState.IDLE)
            await show_main_menu(update, context)
            return
        # Menu button fallback while in BET_REGION → go to IDLE then handle
        if text in MENU_BUTTONS:
            _set_user_state(user_id, UserState.IDLE)
            await main_menu_handler(update, context)
            return
        await update.message.reply_text("Please select a region (MN / MT / MB).", reply_markup=_build_region_kb())
        return

    # ── State: ODI_DATE (Phase 1.1 ReplyKeyboard date picker) ──
    if state == UserState.ODI_DATE:
        # "Today dd/mm" button
        if text.startswith("Today") or text.startswith("today"):
            _set_user_target_date(user_id, _today_iso())
            _set_user_state(user_id, UserState.BET_REGION)
            await _send_menu_message(update, context, "Select region:", _build_region_kb())
            return
        # Date button: "dd/mm"
        if re.match(r"^\d{2}/\d{2}$", text):
            day, month = text.split("/")
            year = date.today().year
            try:
                target_date = date(year, int(month), int(day)).isoformat()
            except ValueError:
                await _send_menu_message(update, context, "❌ Invalid date.", _build_odi_kb())
                return
            _set_user_target_date(user_id, target_date)
            _set_user_state(user_id, UserState.BET_REGION)
            await _send_menu_message(update, context, "Select region:", _build_region_kb())
            return
        # "Set Custom Date" button
        if text.lower() == "set custom date":
            _set_waiting_custom_date(user_id, True)
            await _send_menu_message(update, context, "Please enter date (YYYY-MM-DD):", ReplyKeyboardRemove())
            return
        # "⬅ Back" button
        if text == "⬅ Back":
            _set_user_state(user_id, UserState.IDLE)
            await show_main_menu(update, context)
            return
        # Menu button fallback while in ODI_DATE → go to IDLE then handle
        if text in MENU_BUTTONS:
            _set_user_state(user_id, UserState.IDLE)
            await main_menu_handler(update, context)
            return
        await _send_menu_message(update, context, "Please select a date.", _build_odi_kb())
        return

    # ── State: REPORT_TYPE (Phase 1.2 ReplyKeyboard type picker) ──
    if state == UserState.REPORT_TYPE:
        type_map = {
            REPORT_LABEL_TRANSACTION: REPORT_TYPE_TRANSACTION,
            REPORT_LABEL_SETTLEMENT: REPORT_TYPE_SETTLEMENT,
            REPORT_LABEL_NUMBER_DETAIL: REPORT_TYPE_NUMBER_DETAIL,
            REPORT_LABEL_OVER_LIMIT: REPORT_TYPE_OVER_LIMIT,
        }
        if text in type_map:
            _set_user_state(user_id, UserState.REPORT_DATE)
            user_context[user_id]["report_type"] = type_map[text]
            await _send_menu_message(update, context, "Select date:", _build_report_date_kb())
            return
        if text == "⬅ Back":
            _set_user_state(user_id, UserState.IDLE)
            await show_main_menu(update, context)
            return
        if text in MENU_BUTTONS:
            _set_user_state(user_id, UserState.IDLE)
            await main_menu_handler(update, context)
            return
        await update.message.reply_text("Please select a report type.", reply_markup=_build_report_type_kb())
        return

    # ── State: REPORT_DATE (Phase 1.2 ReplyKeyboard date picker) ──
    if state == UserState.REPORT_DATE:
        report_type = user_context[user_id].get("report_type", REPORT_TYPE_TRANSACTION)
        # "Today dd/mm" button
        if text.startswith("Today") or text.startswith("today"):
            target_date = _today_iso()
            report_text = _generate_report_text(report_type, target_date)
            await _clear_menu_message(update, context)
            if report_text:
                await update.message.reply_text(
                    _as_monospace_html(report_text),
                    parse_mode="HTML",
                    reply_markup=_build_report_action_keyboard(report_type, target_date),
                )
            else:
                await update.message.reply_text(REPORT_COMING_SOON_TEXT, reply_markup=ReplyKeyboardRemove())
                _set_user_state(user_id, UserState.IDLE)
                await show_main_menu(update, context)
            return
        # Date button: "dd/mm"
        if re.match(r"^\d{2}/\d{2}$", text):
            day, month = text.split("/")
            year = date.today().year
            try:
                target_date = date(year, int(month), int(day)).isoformat()
            except ValueError:
                await _send_menu_message(update, context, "❌ Invalid date.", _build_report_date_kb())
                return
            report_text = _generate_report_text(report_type, target_date)
            await _clear_menu_message(update, context)
            if report_text:
                await update.message.reply_text(
                    _as_monospace_html(report_text),
                    parse_mode="HTML",
                    reply_markup=_build_report_action_keyboard(report_type, target_date),
                )
            else:
                await update.message.reply_text(REPORT_COMING_SOON_TEXT, reply_markup=ReplyKeyboardRemove())
                _set_user_state(user_id, UserState.IDLE)
                await show_main_menu(update, context)
            return
        # "⬅ Back" → return to report type selection
        if text == "⬅ Back":
            _set_user_state(user_id, UserState.REPORT_TYPE)
            await _send_menu_message(update, context, "Select report type:", _build_report_type_kb())
            return
        # Menu button fallback
        if text in MENU_BUTTONS:
            _set_user_state(user_id, UserState.IDLE)
            await main_menu_handler(update, context)
            return
        await _send_menu_message(update, context, "Please select a date.", _build_report_date_kb())
        return

    # ── State: ADMIN_WAITING (legacy admin text input) ──
    admin_waiting_action = _get_admin_waiting_action(user_id)
    if admin_waiting_action:
        if not admin_auth_service.is_admin(user_id):
            _set_admin_waiting_action(user_id, None)
            _set_user_state(user_id, UserState.IDLE)
            await update.message.reply_text("您没有权限访问此功能。")
            return

        if text in MENU_BUTTONS:
            _set_admin_waiting_action(user_id, None)
            _set_user_state(user_id, UserState.IDLE)
            await main_menu_handler(update, context)
            return

        try:
            if admin_waiting_action == "ADD_ADMIN":
                if not text.isdigit():
                    await update.message.reply_text("❌ Invalid user id. Please enter digits only.")
                    return
                admin_auth_service.add_admin(text)
                _set_admin_waiting_action(user_id, None)
                await update.message.reply_text(f"✅ Admin added\nUser ID: {text}")
                await update.message.reply_text(text=_build_set_admin_text(), reply_markup=_build_set_admin_keyboard())
                return

            if admin_waiting_action == "REMOVE_ADMIN":
                if not text.isdigit():
                    await update.message.reply_text("❌ Invalid user id. Please enter digits only.")
                    return
                _, message = admin_auth_service.remove_admin(text)
                _set_admin_waiting_action(user_id, None)
                await update.message.reply_text(message)
                await update.message.reply_text(text=_build_set_admin_text(), reply_markup=_build_set_admin_keyboard())
                return

            if admin_waiting_action == "SET_AGENT_COMM":
                normalized = admin_settings_service.set_agent_commission_rate(text)
                _set_admin_waiting_action(user_id, None)
                await update.message.reply_text(f"✅ Agent Commission updated\nCurrent: {normalized}%")
                await update.message.reply_text(text="Agent Comm Setting", reply_markup=_build_agent_comm_keyboard())
                return

            if admin_waiting_action == "SET_BONUS_PAYOUT_BULK":
                admin_settings_service.update_bonus_payout_bulk(text)
                _set_admin_waiting_action(user_id, None)
                await update.message.reply_text("✅ Bonus Payout updated")
                await update.message.reply_text(text=admin_settings_service.format_bonus_payout_text(), reply_markup=_build_bonus_payout_keyboard())
                return

            if admin_waiting_action == "SET_OVER_LIMIT_BULK":
                admin_settings_service.update_limit_bulk(text)
                _set_admin_waiting_action(user_id, None)
                await update.message.reply_text("✅ Over Limit updated")
                await update.message.reply_text(text=admin_settings_service.format_limit_text(), reply_markup=_build_over_limit_keyboard())
                return

            if admin_waiting_action == "SET_CUTOFF_TIME_BULK":
                admin_settings_service.update_cutoff_time_bulk(text)
                _set_admin_waiting_action(user_id, None)
                await update.message.reply_text("✅ Cutoff Time updated")
                await update.message.reply_text(text=admin_settings_service.format_cutoff_time_text(), reply_markup=_build_time_limit_keyboard())
                return
        except Exception as e:
            await update.message.reply_text(f"❌ {str(e)}")
            return

    # ── State: legacy custom date input ──
    if _is_waiting_custom_date(user_id):
        if text in MENU_BUTTONS:
            _set_waiting_custom_date(user_id, False)
            _set_user_state(user_id, UserState.IDLE)
            await main_menu_handler(update, context)
            return
        parsed_date = _parse_custom_date_or_none(text)
        if not parsed_date:
            await update.message.reply_text("❌ Invalid date format.\nPlease use YYYY-MM-DD")
            return
        _set_user_target_date(user_id, parsed_date)
        _set_user_state(user_id, UserState.BET_INPUT)
        _set_user_region(user_id, None)  # force re-select via /mn /mt /mb
        await _clear_menu_message(update, context)
        await update.message.reply_text("Other Day Input", reply_markup=ReplyKeyboardRemove())
        await _send_menu_message(update, context, "Bet", get_bet_menu_keyboard())
        return

    # ── State: RESULT_DATE (Phase 1.3 ReplyKeyboard date picker) ──
    if state == UserState.RESULT_DATE:
        # "Today dd/mm" button
        if text.startswith("Today") or text.startswith("today"):
            draw_date = _today_iso()
            _set_user_result_draw_date(user_id, draw_date)
            _set_user_state(user_id, UserState.RESULT_REGION)
            await _send_menu_message(update, context, "Select region:", _build_result_region_kb())
            return
        # Date button: "dd/mm"
        if re.match(r"^\d{2}/\d{2}$", text):
            day, month = text.split("/")
            year = date.today().year
            try:
                draw_date = date(year, int(month), int(day)).isoformat()
            except ValueError:
                await _send_menu_message(update, context, "❌ Invalid date.", _build_result_date_kb())
                return
            _set_user_result_draw_date(user_id, draw_date)
            _set_user_state(user_id, UserState.RESULT_REGION)
            await _send_menu_message(update, context, "Select region:", _build_result_region_kb())
            return
        # "⬅ Back" button
        if text == "⬅ Back":
            _set_user_state(user_id, UserState.IDLE)
            await show_main_menu(update, context)
            return
        # Menu button fallback while in RESULT_DATE → go to IDLE then handle
        if text in MENU_BUTTONS:
            _set_user_state(user_id, UserState.IDLE)
            await main_menu_handler(update, context)
            return
        await _send_menu_message(update, context, "Please select a date.", _build_result_date_kb())
        return

    # ── State: RESULT_REGION (Phase 1.3 ReplyKeyboard region picker) ──
    if state == UserState.RESULT_REGION:
        region = text.upper()
        if region in VALID_REGIONS:
            _set_user_result_region(user_id, region)
            draw_date = _get_user_result_draw_date(user_id)
            if not draw_date:
                draw_date = _today_iso()
            # Fetch and display result
            result_data = result_query_service.get_or_fetch(draw_date, region)
            meta = result_data.get("meta")
            items = result_data.get("items", [])
            message_text = format_result_message(meta, items)
            await _clear_menu_message(update, context)
            await update.message.reply_text(_as_monospace_html(message_text), parse_mode="HTML", reply_markup=ReplyKeyboardRemove())
            # Show result action keyboard (ReplyKeyboard style)
            await _send_menu_message(update, context, "Result actions:", _build_result_region_kb())
            return
        if text == "⬅ Back":
            _set_user_state(user_id, UserState.RESULT_DATE)
            await _send_menu_message(update, context, _build_result_menu_text(), _build_result_date_kb())
            return
        # Menu button fallback while in RESULT_REGION → go to IDLE then handle
        if text in MENU_BUTTONS:
            _set_user_state(user_id, UserState.IDLE)
            await main_menu_handler(update, context)
            return
        await update.message.reply_text("Please select a region (MN / MT / MB).", reply_markup=_build_result_region_kb())
        return

    # ── State: ADMIN_MENU (Phase 1.4 ReplyKeyboard admin menu) ──
    if state == UserState.ADMIN_MENU:
        normalized_text = re.sub(r"\s+", " ", text).strip().lower()

        if (
            normalized_text == "1. agent comm setting"
            or normalized_text.endswith("agent comm setting")
        ):
            await _send_menu_message(update, context, "Agent Comm Setting", _build_agent_comm_keyboard())
            return

        if (
            normalized_text == "2. bonus payout setting"
            or normalized_text.endswith("bonus payout setting")
        ):
            await _send_menu_message(update, context, "Bonus Payout Setting", _build_bonus_payout_keyboard())
            return

        if (
            normalized_text == "3. over limit setting"
            or normalized_text.endswith("over limit setting")
        ):
            await _send_menu_message(update, context, "Over Limit Setting", _build_over_limit_keyboard())
            return

        if (
            normalized_text == "4. notifications"
            or normalized_text.endswith("notifications")
        ):
            await _send_menu_message(update, context, "Notifications", _build_notifications_keyboard())
            return

        if (
            normalized_text == "5. bet time limit"
            or normalized_text.endswith("bet time limit")
        ):
            await _send_menu_message(update, context, "Bet Time Limit", _build_time_limit_keyboard())
            return

        if (
            normalized_text == "6. system time zone"
            or normalized_text.endswith("system time zone")
            or normalized_text == "6. system setting"
            or normalized_text.endswith("system setting")
        ):
            await _send_menu_message(update, context, "System Time Zone", _build_system_timezone_keyboard())
            return

        if (
            normalized_text == "7. set admin"
            or normalized_text.endswith("set admin")
        ):
            await _send_menu_message(update, context, _build_set_admin_text(), _build_set_admin_keyboard())
            return

        if text == "⬅ Back":
            _set_user_state(user_id, UserState.IDLE)
            await show_main_menu(update, context)
            return

        if text in MENU_BUTTONS:
            _set_user_state(user_id, UserState.IDLE)
            await main_menu_handler(update, context)
            return

        await _send_menu_message(update, context, "Please select an admin option.", _build_admin_menu_kb())
        return

    # ── Main menu buttons (IDLE or fallback) ──
    if text in MENU_BUTTONS:
        await main_menu_handler(update, context)
        return

    # ── Delete command ──
    if text.lower().startswith("delete"):
        parts = text.split()
        if len(parts) < 2:
            await update.message.reply_text("❌ Usage: delete N1")
            return
        ticket_no = parts[1].upper()
        target_date = _get_user_target_date(user_id)
        _, response_text = delete_ticket(ticket_no, target_date)
        await _clear_menu_message(update, context)
        await update.message.reply_text(_as_monospace_html(_build_delete_success_message(response_text)), parse_mode="HTML", reply_markup=ReplyKeyboardRemove())
        return

    # ── Bet input (state BET_INPUT or legacy region set) ──
    current_region = _get_user_region(user_id)
    if current_region:
        await bet_handler(update, context)
        return

    await _clear_menu_message(update, context)
    await update.message.reply_text("Please select region first.\nUse /mn /mt /mb", reply_markup=ReplyKeyboardRemove())


async def bet_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.effective_user:
        return
    user_id = update.effective_user.id
    text = update.message.text
    region_group = _get_user_region(user_id)
    target_date = _get_user_target_date(user_id)
    if not region_group:
        await _clear_menu_message(update, context)
        await update.message.reply_text("Please select region first.\nUse /mn /mt /mb", reply_markup=ReplyKeyboardRemove())
        return
    try:
        _, response_text = process_bet_message(user_id=str(user_id), region_group=region_group, text=text, target_date=target_date)
        await _clear_menu_message(update, context)
        await update.message.reply_text(_as_monospace_html(response_text), parse_mode="HTML", reply_markup=ReplyKeyboardRemove())
    except Exception as e:
        await update.message.reply_text(f"System Error: {str(e)}")


# =========================================================
# App builder
# =========================================================
def build_application() -> Application:
    log_step("🤖 Building Telegram application ...")
    application = ApplicationBuilder().token(BOT_TOKEN).post_init(post_init).build()

    log_step("🧩 Registering handlers ...")
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("result", result_entry_command))
    application.add_handler(CommandHandler("myid", myid_command))
    application.add_handler(CommandHandler("mn", mn_command))
    application.add_handler(CommandHandler("mt", mt_command))
    application.add_handler(CommandHandler("mb", mb_command))
    application.add_handler(CommandHandler("delete", delete_command))
    application.add_handler(CommandHandler("settlement", settlement_today_command))

    application.add_handler(CallbackQueryHandler(handle_report_menu, pattern=f"^{REPORT_CALLBACK_MENU}$"))
    application.add_handler(CallbackQueryHandler(handle_report_type, pattern=f"^{REPORT_CALLBACK_TYPE_PREFIX}"))
    application.add_handler(CallbackQueryHandler(handle_report_date, pattern=f"^{REPORT_CALLBACK_DATE_PREFIX}"))
    application.add_handler(CallbackQueryHandler(handle_report_export, pattern=f"^{REPORT_CALLBACK_EXPORT_PREFIX}"))
    application.add_handler(CallbackQueryHandler(handle_report_menu, pattern=f"^{REPORT_CALLBACK_BACK_TO_MENU}$"))
    application.add_handler(CallbackQueryHandler(handle_report_close, pattern=f"^{REPORT_CALLBACK_CLOSE}$"))

    application.add_handler(CallbackQueryHandler(handle_admin_menu, pattern=f"^{CALLBACK_ADMIN_MENU}$"))
    application.add_handler(CallbackQueryHandler(handle_admin_set_admin_menu, pattern=f"^{CALLBACK_ADMIN_SET_ADMIN}$"))
    application.add_handler(CallbackQueryHandler(handle_admin_view_admins, pattern=f"^{CALLBACK_ADMIN_VIEW_ADMINS}$"))
    application.add_handler(CallbackQueryHandler(handle_admin_add_admin_prompt, pattern=f"^{CALLBACK_ADMIN_ADD_ADMIN}$"))
    application.add_handler(CallbackQueryHandler(handle_admin_remove_admin_prompt, pattern=f"^{CALLBACK_ADMIN_REMOVE_ADMIN}$"))
    application.add_handler(CallbackQueryHandler(handle_admin_agent_menu, pattern=f"^{CALLBACK_ADMIN_AGENT_MENU}$"))
    application.add_handler(CallbackQueryHandler(handle_admin_agent_view, pattern=f"^{CALLBACK_ADMIN_AGENT_VIEW}$"))
    application.add_handler(CallbackQueryHandler(handle_admin_agent_edit, pattern=f"^{CALLBACK_ADMIN_AGENT_EDIT}$"))
    application.add_handler(CallbackQueryHandler(handle_admin_bonus_menu, pattern=f"^{CALLBACK_ADMIN_BONUS_MENU}$"))
    application.add_handler(CallbackQueryHandler(handle_admin_bonus_view, pattern=f"^{CALLBACK_ADMIN_BONUS_VIEW}$"))
    application.add_handler(CallbackQueryHandler(handle_admin_bonus_edit, pattern=f"^{CALLBACK_ADMIN_BONUS_EDIT}$"))
    application.add_handler(CallbackQueryHandler(handle_admin_limit_menu, pattern=f"^{CALLBACK_ADMIN_LIMIT_MENU}$"))
    application.add_handler(CallbackQueryHandler(handle_admin_limit_view, pattern=f"^{CALLBACK_ADMIN_LIMIT_VIEW}$"))
    application.add_handler(CallbackQueryHandler(handle_admin_limit_edit, pattern=f"^{CALLBACK_ADMIN_LIMIT_EDIT}$"))
    application.add_handler(CallbackQueryHandler(handle_admin_limit_action_menu, pattern=f"^{CALLBACK_ADMIN_LIMIT_ACTION_MENU}$"))
    application.add_handler(CallbackQueryHandler(handle_admin_limit_action_accept, pattern=f"^{CALLBACK_ADMIN_LIMIT_ACTION_ACCEPT}$"))
    application.add_handler(CallbackQueryHandler(handle_admin_limit_action_reject, pattern=f"^{CALLBACK_ADMIN_LIMIT_ACTION_REJECT}$"))
    application.add_handler(CallbackQueryHandler(handle_admin_notifications_menu, pattern=f"^{CALLBACK_ADMIN_NOTIFICATIONS_MENU}$"))
    application.add_handler(CallbackQueryHandler(handle_admin_notifications_view, pattern=f"^{CALLBACK_ADMIN_NOTIFICATIONS_VIEW}$"))
    application.add_handler(CallbackQueryHandler(handle_admin_notifications_on, pattern=f"^{CALLBACK_ADMIN_NOTIFICATIONS_ON}$"))
    application.add_handler(CallbackQueryHandler(handle_admin_notifications_off, pattern=f"^{CALLBACK_ADMIN_NOTIFICATIONS_OFF}$"))
    application.add_handler(CallbackQueryHandler(handle_admin_time_limit_menu, pattern=f"^{CALLBACK_ADMIN_TIME_LIMIT_MENU}$"))
    application.add_handler(CallbackQueryHandler(handle_admin_time_limit_view, pattern=f"^{CALLBACK_ADMIN_TIME_LIMIT_VIEW}$"))
    application.add_handler(CallbackQueryHandler(handle_admin_time_limit_edit, pattern=f"^{CALLBACK_ADMIN_TIME_LIMIT_EDIT}$"))
    application.add_handler(CallbackQueryHandler(handle_admin_system_tz_menu, pattern=f"^{CALLBACK_ADMIN_SYSTEM_TZ_MENU}$"))
    application.add_handler(CallbackQueryHandler(handle_admin_system_tz_view, pattern=f"^{CALLBACK_ADMIN_SYSTEM_TZ_VIEW}$"))
    application.add_handler(CallbackQueryHandler(handle_admin_system_tz_kl, pattern=f"^{CALLBACK_ADMIN_SYSTEM_TZ_KL}$"))
    application.add_handler(CallbackQueryHandler(handle_admin_system_tz_hcm, pattern=f"^{CALLBACK_ADMIN_SYSTEM_TZ_HCM}$"))
    application.add_handler(CallbackQueryHandler(handle_admin_back, pattern=f"^{CALLBACK_ADMIN_BACK}$"))
    application.add_handler(CallbackQueryHandler(handle_admin_close, pattern=f"^{CALLBACK_ADMIN_CLOSE}$"))

    application.add_handler(CallbackQueryHandler(handle_other_day_menu, pattern=f"^{CALLBACK_ODI_MENU}$"))
    application.add_handler(CallbackQueryHandler(handle_other_day_select_date, pattern=f"^{CALLBACK_ODI_DATE_PREFIX}"))
    application.add_handler(CallbackQueryHandler(handle_other_day_set_custom, pattern=f"^{CALLBACK_ODI_SET_CUSTOM}$"))
    application.add_handler(CallbackQueryHandler(handle_other_day_set_today, pattern=f"^{CALLBACK_ODI_SET_TODAY}$"))
    application.add_handler(CallbackQueryHandler(handle_other_day_close, pattern=f"^{CALLBACK_ODI_CLOSE}$"))

    # Keep old InlineKeyboard handlers as fallback
    application.add_handler(CallbackQueryHandler(handle_result_menu, pattern=f"^{CALLBACK_RESULT_MENU}$"))
    application.add_handler(CallbackQueryHandler(handle_result_date_select, pattern=f"^{CALLBACK_RESULT_DATE_PREFIX}"))
    application.add_handler(CallbackQueryHandler(handle_result_view, pattern=f"^{CALLBACK_RESULT_VIEW_PREFIX}"))
    application.add_handler(CallbackQueryHandler(handle_result_refresh, pattern=f"^{CALLBACK_RESULT_REFRESH_PREFIX}"))
    application.add_handler(CallbackQueryHandler(handle_result_change_date, pattern=f"^{CALLBACK_RESULT_CHANGE_DATE}$"))
    application.add_handler(CallbackQueryHandler(handle_result_close, pattern=f"^{CALLBACK_RESULT_CLOSE}$"))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_router))

    log_step("✅ Handlers registered")
    return application


if __name__ == "__main__":
    try:
        validate_environment()
        initialize_database()
        application = build_application()
        log_step("▶ Starting polling ...")
        application.run_polling()
    except Exception as e:
        log_step(f"❌ Startup failed: {e}")
        sys.exit(1)
