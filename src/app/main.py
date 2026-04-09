import os
import re
import sys
import traceback
from datetime import datetime, timedelta, date, time, timezone
from html import escape
from pathlib import Path

from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, Update
from telegram.ext import (
    Application,
    ApplicationHandlerStop,
    ApplicationBuilder,
    CallbackQueryHandler,
    ChatMemberHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    TypeHandler,
    filters,
)

# ===========================================
# 多租户配置支持
# ===========================================
import argparse
import json

def load_config(config_dir=None):
    """
    从指定目录加载配置
    
    参数:
        config_dir: 配置目录路径，如果为None则使用当前目录
    
    返回:
        dict: 配置字典
    """
    if config_dir:
        config_path = Path(config_dir)
    else:
        config_path = Path.cwd()
    
    # 加载.env文件
    env_file = config_path / ".env"
    if not env_file.exists():
        raise FileNotFoundError(f"配置文件不存在: {env_file}")
    
    # 直接读取.env文件，避免环境变量污染
    env_vars = {}
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()
    
    # 读取配置
    allowed_group_id_raw = env_vars.get('ALLOWED_GROUP_ID', '').strip()
    allowed_group_id = None
    allowed_group_id_error = None
    if not allowed_group_id_raw:
        allowed_group_id_error = "missing_allowed_group_id"
    else:
        try:
            allowed_group_id = int(allowed_group_id_raw)
        except ValueError:
            allowed_group_id_error = "invalid_allowed_group_id"

    config = {
        'BOT_TOKEN': env_vars.get('BOT_TOKEN'),
        'DB_PATH': env_vars.get('DB_PATH', 'data/lotto.db'),
        'LOG_PATH': env_vars.get('LOG_PATH', 'app.log'),
        'CLIENT_NAME': env_vars.get('CLIENT_NAME', 'default_client'),
        'TIMEZONE': env_vars.get('TIMEZONE', 'Asia/Ho_Chi_Minh'),
        'DEFAULT_LANGUAGE': env_vars.get('DEFAULT_LANGUAGE', 'vi'),
        'ADMIN_CHAT_ID': env_vars.get('ADMIN_CHAT_ID'),
        'DEFAULT_ADMIN_USER_IDS': env_vars.get('DEFAULT_ADMIN_USER_IDS', ''),
        'ALLOWED_GROUP_ID': allowed_group_id,
        'ALLOWED_GROUP_ID_RAW': allowed_group_id_raw,
        'ALLOWED_GROUP_ID_ERROR': allowed_group_id_error,
    }
    
    # 验证必要配置
    if not config['BOT_TOKEN'] or config['BOT_TOKEN'] == 'YOUR_BOT_TOKEN_HERE':
        raise ValueError("BOT_TOKEN未配置或仍为模板值")
    
    # 加载settings.json（可选）
    settings_file = config_path / "settings.json"
    if settings_file.exists():
        try:
            with open(settings_file, 'r', encoding='utf-8') as f:
                config['settings'] = json.load(f)
        except json.JSONDecodeError:
            config['settings'] = {}
    else:
        config['settings'] = {}
    
    return config

from src.bot.menus.bet_menu import get_bet_menu_keyboard
from src.bot.menus.main_menu import get_main_menu_keyboard, get_main_menu_button_labels
from src.i18n.translator import t
from src.modules.admin.services.admin_auth_service import AdminAuthService
from src.modules.admin.services.admin_settings_service import AdminSettingsService
from src.modules.bet.services.bet_message_service import (
    process_bet_message,
    init_database,
    delete_ticket,
)
from src.modules.customer.repositories.agent_customer_repository import AgentCustomerRepository
from src.modules.customer.repositories.user_preference_repository import UserPreferenceRepository
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


AUTO_FETCH_TZ = timezone(timedelta(hours=8))
AUTO_FETCH_START_TIMES = {
    "MN": time(hour=17, minute=28),
    "MT": time(hour=18, minute=28),
    "MB": time(hour=19, minute=28),
}
AUTO_FETCH_COMPLETE_KEY = "auto_result_fetch_completed"
AUTO_FETCH_LAST_LOG_KEY = "auto_result_fetch_last_log"


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
# Union of main menu button labels for all supported languages — used for fallback routing.
# Covers all three langs so text in MENU_BUTTONS catches presses regardless of user language.
MENU_BUTTONS: set[str] = set(
    get_main_menu_button_labels("en") +
    get_main_menu_button_labels("zh") +
    get_main_menu_button_labels("vi")
)

VERSION_FILE = Path("VERSION.txt")

CALLBACK_LANG_SET_PREFIX = "lang_set:"

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
user_last_status_message = {}


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


async def _delete_last_status_message(context: ContextTypes.DEFAULT_TYPE, chat_id: int, user_id: int) -> None:
    last_message_id = user_last_status_message.get(user_id)
    if not last_message_id:
        return
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=last_message_id)
    except Exception:
        pass
    finally:
        user_last_status_message.pop(user_id, None)


async def _send_status_message(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, reply_markup=None, parse_mode=None) -> None:
    if not update.message or not update.effective_user or not update.effective_chat:
        return
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    await _delete_last_status_message(context, chat_id, user_id)
    sent = await update.message.reply_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
    user_last_status_message[user_id] = sent.message_id


async def _clear_transient_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_user or not update.effective_chat:
        return
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    await _delete_last_menu_message(context, chat_id, user_id)
    await _delete_last_status_message(context, chat_id, user_id)


result_query_service = ResultQueryService()
result_fetch_service = ResultFetchService()

transaction_report_service = TransactionReportService()
number_detail_report_service = NumberDetailReportService()
settlement_report_service = SettlementReportService()
over_limit_report_service = OverLimitReportService()

admin_auth_service = None
admin_settings_service = None
agent_customer_repository = None
user_pref_repo = None


def log_step(message: str) -> None:
    print(message, flush=True)


def _get_system_timezone():
    try:
        return admin_settings_service.get_timezone()
    except Exception:
        return timezone(timedelta(hours=8))


def _now_local() -> datetime:
    return datetime.now(_get_system_timezone())


def _today_local_date() -> date:
    return _now_local().date()

def _auto_fetch_completion_map(application: Application) -> dict[str, str]:
    return application.bot_data.setdefault(AUTO_FETCH_COMPLETE_KEY, {})


def _auto_fetch_last_log_map(application: Application) -> dict[str, str]:
    return application.bot_data.setdefault(AUTO_FETCH_LAST_LOG_KEY, {})


def _today_kl_iso() -> str:
    return datetime.now(AUTO_FETCH_TZ).date().isoformat()


def _should_start_auto_fetch(region_group: str, now_kl: datetime) -> bool:
    start_time = AUTO_FETCH_START_TIMES[region_group]
    return now_kl.time() >= start_time


async def auto_fetch_results_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    application = context.application
    now_kl = datetime.now(AUTO_FETCH_TZ)
    target_date = now_kl.date().isoformat()

    completed = _auto_fetch_completion_map(application)
    last_log = _auto_fetch_last_log_map(application)

    for region_group in ("MN", "MT", "MB"):
        if not _should_start_auto_fetch(region_group, now_kl):
            continue

        if completed.get(region_group) == target_date:
            continue

        try:
            fetch_result = result_fetch_service.fetch_and_store(target_date, region_group)
            is_complete = result_fetch_service.is_result_complete(target_date, region_group)

            if is_complete:
                completed[region_group] = target_date
                log_step(
                    f"✅ Auto result fetch complete | {region_group} | {target_date} | status={fetch_result.get('status')}"
                )
                continue

            log_key = f"{target_date}:{region_group}"
            current_minute = now_kl.strftime("%Y-%m-%d %H:%M")
            if last_log.get(log_key) != current_minute:
                last_log[log_key] = current_minute
                log_step(
                    f"⏳ Auto result fetch pending | {region_group} | {target_date} | status={fetch_result.get('status')}"
                )
        except Exception as exc:
            log_key = f"error:{target_date}:{region_group}"
            current_minute = now_kl.strftime("%Y-%m-%d %H:%M")
            if last_log.get(log_key) != current_minute:
                last_log[log_key] = current_minute
                log_step(f"⚠ Auto result fetch failed | {region_group} | {target_date} | {exc}")


# =========================================================
# Phase 1.1: ReplyKeyboard Builders
# =========================================================
def _build_main_menu_kb(user_id: int | None = None) -> ReplyKeyboardMarkup:
    """Reusable ReplyKeyboard for main menu state (IDLE)."""
    return get_main_menu_keyboard(lang=_get_user_lang(user_id))

def _build_region_kb(lang: str = "en") -> ReplyKeyboardMarkup:
    """ReplyKeyboard for region selection state (BET_REGION)."""
    return ReplyKeyboardMarkup(
        [[KeyboardButton("MN"), KeyboardButton("MT"), KeyboardButton("MB")],
         [KeyboardButton(t("BTN_BACK", lang=lang))]],
        resize_keyboard=True,
    )

def _build_odi_kb(lang: str = "en") -> ReplyKeyboardMarkup:
    """ReplyKeyboard for Other Day Input date selection (ODI_DATE)."""
    today = _today_local_date()
    prev_dates = [today - timedelta(days=i) for i in range(3, 0, -1)]
    next_dates = [today + timedelta(days=i) for i in range(1, 4)]
    row_prev = [KeyboardButton(d.strftime("%d/%m")) for d in prev_dates]
    row_today = [KeyboardButton(t("BTN_TODAY", lang=lang, date=today.strftime("%d/%m")))]
    row_next = [KeyboardButton(d.strftime("%d/%m")) for d in next_dates]
    return ReplyKeyboardMarkup(
        [row_prev, row_today, row_next, [KeyboardButton(t("BTN_SET_CUSTOM_DATE", lang=lang)), KeyboardButton(t("BTN_BACK", lang=lang))]],
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


def _get_user_lang(user_id: int | None) -> str:
    if user_id is None:
        return "en"
    _ensure_user_context(user_id)
    if "lang" not in user_context[user_id]:
        user_context[user_id]["lang"] = user_pref_repo.get_lang(str(user_id))
    return user_context[user_id]["lang"]


def _set_user_lang(user_id: int, lang: str) -> None:
    _ensure_user_context(user_id)
    user_context[user_id]["lang"] = lang
    user_pref_repo.set_lang(str(user_id), lang)


def _parse_allowed_group_id(raw_value: str | None) -> tuple[int | None, str | None]:
    value = (raw_value or "").strip()
    if not value:
        return None, "missing_allowed_group_id"
    try:
        return int(value), None
    except ValueError:
        return None, "invalid_allowed_group_id"


def _get_default_language() -> str:
    lang = os.getenv("DEFAULT_LANGUAGE", "en")
    return lang if lang in {"en", "zh", "vi"} else "en"


def _resolve_scope_lang(update: Update) -> str:
    if update.effective_user:
        return _get_user_lang(update.effective_user.id)
    return _get_default_language()


def _get_chat_scope_config() -> dict[str, object]:
    allowed_group_id, allowed_group_error = _parse_allowed_group_id(os.getenv("ALLOWED_GROUP_ID"))
    return {
        "bot_label": os.getenv("CLIENT_NAME", "default_client"),
        "allowed_group_id": allowed_group_id,
        "allowed_group_error": allowed_group_error,
    }


def _log_chat_scope_rejection(
    *,
    reason: str,
    bot_label: str,
    chat_id: int | None,
    chat_type: str | None,
) -> None:
    log_step(
        f"⚠ Chat scope rejected | bot={bot_label} | chat_id={chat_id if chat_id is not None else 'N/A'} "
        f"| chat_type={chat_type or 'N/A'} | reason={reason}"
    )


async def _notify_scope_rejection(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    translation_key: str,
    lang: str,
) -> None:
    message_text = t(translation_key, lang=lang)
    query = update.callback_query
    if query:
        try:
            await query.answer(text=message_text, show_alert=True)
            return
        except Exception:
            pass

    if update.effective_message:
        try:
            await update.effective_message.reply_text(message_text)
            return
        except Exception:
            pass

    if update.effective_chat:
        try:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=message_text)
        except Exception:
            pass


async def enforce_chat_scope(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    scope_config = context.application.bot_data.get("chat_scope_config") or _get_chat_scope_config()
    bot_label = str(scope_config.get("bot_label", "default_client"))
    allowed_group_id = scope_config.get("allowed_group_id")
    allowed_group_error = scope_config.get("allowed_group_error")

    chat = update.effective_chat
    if chat is None:
        _log_chat_scope_rejection(
            reason="no_chat_context",
            bot_label=bot_label,
            chat_id=None,
            chat_type=None,
        )
        raise ApplicationHandlerStop

    chat_id = chat.id
    chat_type = chat.type
    lang = _resolve_scope_lang(update)

    if chat_type == "private":
        _log_chat_scope_rejection(
            reason="private",
            bot_label=bot_label,
            chat_id=chat_id,
            chat_type=chat_type,
        )
        await _notify_scope_rejection(update, context, "BOT_SCOPE_PRIVATE_ONLY", lang)
        raise ApplicationHandlerStop

    if chat_type not in {"group", "supergroup"}:
        _log_chat_scope_rejection(
            reason="unsupported_chat_type",
            bot_label=bot_label,
            chat_id=chat_id,
            chat_type=chat_type,
        )
        raise ApplicationHandlerStop

    if allowed_group_error == "missing_allowed_group_id":
        _log_chat_scope_rejection(
            reason="missing_allowed_group_id",
            bot_label=bot_label,
            chat_id=chat_id,
            chat_type=chat_type,
        )
        await _notify_scope_rejection(update, context, "BOT_SCOPE_UNAUTHORIZED_GROUP", lang)
        raise ApplicationHandlerStop

    if allowed_group_error == "invalid_allowed_group_id":
        _log_chat_scope_rejection(
            reason="invalid_allowed_group_id",
            bot_label=bot_label,
            chat_id=chat_id,
            chat_type=chat_type,
        )
        await _notify_scope_rejection(update, context, "BOT_SCOPE_UNAUTHORIZED_GROUP", lang)
        raise ApplicationHandlerStop

    if chat_id != allowed_group_id:
        _log_chat_scope_rejection(
            reason="unauthorized_group",
            bot_label=bot_label,
            chat_id=chat_id,
            chat_type=chat_type,
        )
        await _notify_scope_rejection(update, context, "BOT_SCOPE_UNAUTHORIZED_GROUP", lang)
        raise ApplicationHandlerStop

    query = update.callback_query
    if query and query.data and str(query.data).startswith("result:"):
        log_step(
            f"🔎 Result callback received | bot={bot_label} | chat_id={chat_id} "
            f"| user_id={query.from_user.id if query.from_user else 'N/A'} | data={query.data}"
        )


def validate_environment() -> None:
    bot_token = os.getenv("BOT_TOKEN")
    admin_chat_id = os.getenv("ADMIN_CHAT_ID")
    default_admin_user_ids = os.getenv("DEFAULT_ADMIN_USER_IDS", "")
    client_name = os.getenv("CLIENT_NAME", "default_client")
    allowed_group_id, allowed_group_error = _parse_allowed_group_id(os.getenv("ALLOWED_GROUP_ID"))

    log_step("⚙ Loading .env ...")
    if os.path.exists(".env"):
        log_step("✅ .env file detected")
    else:
        log_step("⚠ .env file not found, continuing with system environment variables")

    log_step("🔐 Checking BOT_TOKEN ...")
    if not bot_token:
        log_step("❌ BOT_TOKEN is missing")
        raise RuntimeError("BOT_TOKEN is missing in .env or environment variables")
    log_step("✅ BOT_TOKEN loaded")

    if admin_chat_id:
        log_step(f"✅ ADMIN_CHAT_ID loaded: {admin_chat_id}")
    else:
        log_step("⚠ ADMIN_CHAT_ID not set, startup Telegram notification will be skipped")

    if default_admin_user_ids:
        log_step(f"✅ DEFAULT_ADMIN_USER_IDS loaded: {default_admin_user_ids}")
    else:
        log_step("⚠ DEFAULT_ADMIN_USER_IDS not set")

    if allowed_group_error == "missing_allowed_group_id":
        log_step(f"⚠ ALLOWED_GROUP_ID missing | bot={client_name} | all group updates will be rejected")
    elif allowed_group_error == "invalid_allowed_group_id":
        log_step(
            f"❌ ALLOWED_GROUP_ID invalid | bot={client_name} | raw={os.getenv('ALLOWED_GROUP_ID', '')} "
            f"| all group updates will be rejected"
        )
    else:
        log_step(f"✅ ALLOWED_GROUP_ID loaded | bot={client_name} | chat_id={allowed_group_id}")


def initialize_database() -> None:
    global admin_auth_service, admin_settings_service, agent_customer_repository, user_pref_repo

    log_step("🗄 Initializing database ...")

    # 依赖环境变量的服务必须在配置加载后初始化
    if admin_auth_service is None:
        admin_auth_service = AdminAuthService(default_admin_ids_str=os.getenv("DEFAULT_ADMIN_USER_IDS", ""))
    if admin_settings_service is None:
        admin_settings_service = AdminSettingsService()
    if agent_customer_repository is None:
        agent_customer_repository = AgentCustomerRepository()
    if user_pref_repo is None:
        user_pref_repo = UserPreferenceRepository()

    init_database()
    admin_auth_service.init_and_sync()
    admin_settings_service.init_and_sync()
    agent_customer_repository.init_table()
    user_pref_repo.init_table()
    log_step("✅ Database ready")


async def post_init(application: Application) -> None:
    admin_chat_id = os.getenv("ADMIN_CHAT_ID")

    log_step("🤖 Handlers ready")
    log_step(f"🚀 M33 Lotto Bot started at {_now_local().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        from telegram import BotCommand, BotCommandScopeDefault, BotCommandScopeAllGroupChats, BotCommandScopeChat
        from src.i18n.translator import t

        def _cmd_list(lang: str) -> list[BotCommand]:
            return [
                BotCommand("start",      t("CMD_START",      lang)),
                BotCommand("mn",         t("CMD_MN",         lang)),
                BotCommand("mt",         t("CMD_MT",         lang)),
                BotCommand("mb",         t("CMD_MB",         lang)),
                BotCommand("settlement", t("CMD_SETTLEMENT", lang)),
            ]

        async def _register_chat_commands(chat_id: int, lang: str) -> None:
            commands = _cmd_list(lang)
            scope = BotCommandScopeChat(chat_id)
            await application.bot.set_my_commands(commands, scope=scope)
            for forced_lang in ("en", "zh", "vi"):
                await application.bot.set_my_commands(
                    commands,
                    scope=scope,
                    language_code=forced_lang,
                )

        application.bot_data["register_chat_commands"] = _register_chat_commands

        # fallback (no language_code) — shown when user's device lang has no match
        await application.bot.set_my_commands(_cmd_list("en"))
        # per-language overrides (Default scope — private chats + fallback)
        for lang, tg_lang in (("en", "en"), ("zh", "zh"), ("vi", "vi")):
            await application.bot.set_my_commands(
                _cmd_list(lang),
                language_code=tg_lang,
            )
        # AllGroupChats scope — ensures blue Menu button appears in group chats
        await application.bot.set_my_commands(_cmd_list("en"), scope=BotCommandScopeAllGroupChats())
        for lang, tg_lang in (("en", "en"), ("zh", "zh"), ("vi", "vi")):
            await application.bot.set_my_commands(
                _cmd_list(lang),
                scope=BotCommandScopeAllGroupChats(),
                language_code=tg_lang,
            )
        log_step("✅ Command menu registered (en / zh / vi) — Default + AllGroupChats")
    except Exception as e:
        log_step(f"⚠ Failed to register command menu: {e}")

    if application.job_queue is not None:
        application.job_queue.run_repeating(
            auto_fetch_results_job,
            interval=60,
            first=5,
            name="auto_fetch_results_job",
        )
        log_step("✅ Auto result fetch scheduler started (every 1 minute)")

    if not admin_chat_id:
        return

    try:
        await application.bot.send_message(
            chat_id=admin_chat_id,
            text=(
                "🚀 M33 Lotto Bot 已上线\n"
                f"🕒 Start Time: {_now_local().strftime('%Y-%m-%d %H:%M:%S')}\n"
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
    return _today_local_date().isoformat()


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
    lang = _get_user_lang(user_id)
    target_date = _get_user_target_date(user_id)
    base = "\n".join([
        t("BET_MODE_ACTIVE", lang=lang, region=region),
        t("LABEL_DATE", lang=lang, date=target_date),
    ])

    try:
        target_date_obj = datetime.strptime(target_date, "%Y-%m-%d").date()
        allowed_regions = get_allowed_regions(target_date_obj, region)
    except Exception:
        allowed_regions = []

    region = str(region).upper()
    if region in {"MN", "MT"} and allowed_regions:
        region_codes = ", ".join(code.upper() for code in allowed_regions)
        if target_date == _today_iso():
            return f"{base} {t('LABEL_TODAY_SUFFIX', lang=lang)}\n({region_codes})"
        return f"{base}\n({region_codes})"

    if target_date == _today_iso():
        return f"{base} {t('LABEL_TODAY_SUFFIX', lang=lang)}"
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
            t("INFO_TITLE"),
            "",
            t("INFO_REGION_CODE"),
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
            t("INFO_FURTHER"),
            t("INFO_TELEGRAM"),
            t("INFO_VERSION", version=version),
        ]
    )


def _as_monospace_html(text: str) -> str:
    return f"<pre>{escape(str(text))}</pre>"


def _build_report_type_kb(lang: str = "en") -> ReplyKeyboardMarkup:
    """ReplyKeyboard for report type selection (REPORT_TYPE)."""
    return ReplyKeyboardMarkup(
        [[KeyboardButton(t("REPORT_LABEL_TRANSACTION", lang=lang)), KeyboardButton(t("REPORT_LABEL_SETTLEMENT", lang=lang))],
         [KeyboardButton(t("REPORT_LABEL_NUMBER_DETAIL", lang=lang)), KeyboardButton(t("REPORT_LABEL_OVER_LIMIT", lang=lang))],
         [KeyboardButton(t("BTN_BACK", lang=lang))]],
        resize_keyboard=True,
    )

def _build_report_date_kb(lang: str = "en") -> ReplyKeyboardMarkup:
    """ReplyKeyboard for report date selection (REPORT_DATE)."""
    today = _today_local_date()
    dates = [today - timedelta(days=i) for i in range(7)]
    row1 = [KeyboardButton(t("BTN_TODAY", lang=lang, date=dates[0].strftime("%d/%m")))]
    row2 = [KeyboardButton(d.strftime("%d/%m")) for d in dates[1:3]]
    row3 = [KeyboardButton(d.strftime("%d/%m")) for d in dates[3:5]]
    row4 = [KeyboardButton(d.strftime("%d/%m")) for d in dates[5:7]]
    return ReplyKeyboardMarkup(
        [row1, row2, row3, row4, [KeyboardButton(t("BTN_BACK", lang=lang))]],
        resize_keyboard=True,
    )


# =========================================================
# Report helpers
# =========================================================
def _build_report_menu_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(t("REPORT_LABEL_TRANSACTION", lang=lang), callback_data=f"{REPORT_CALLBACK_TYPE_PREFIX}{REPORT_TYPE_TRANSACTION}"),
            InlineKeyboardButton(t("REPORT_LABEL_SETTLEMENT", lang=lang), callback_data=f"{REPORT_CALLBACK_TYPE_PREFIX}{REPORT_TYPE_SETTLEMENT}"),
        ],
        [
            InlineKeyboardButton(t("REPORT_LABEL_NUMBER_DETAIL", lang=lang), callback_data=f"{REPORT_CALLBACK_TYPE_PREFIX}{REPORT_TYPE_NUMBER_DETAIL}"),
            InlineKeyboardButton(t("REPORT_LABEL_OVER_LIMIT", lang=lang), callback_data=f"{REPORT_CALLBACK_TYPE_PREFIX}{REPORT_TYPE_OVER_LIMIT}"),
        ],
        [InlineKeyboardButton(t("BTN_CLOSE", lang=lang), callback_data=REPORT_CALLBACK_CLOSE)],
    ]
    return InlineKeyboardMarkup(keyboard)


def _build_report_date_text(report_type: str, lang: str = "en") -> str:
    label_map = {
        REPORT_TYPE_TRANSACTION: t("REPORT_LABEL_TRANSACTION", lang=lang),
        REPORT_TYPE_SETTLEMENT: t("REPORT_LABEL_SETTLEMENT", lang=lang),
        REPORT_TYPE_NUMBER_DETAIL: t("REPORT_LABEL_NUMBER_DETAIL", lang=lang),
        REPORT_TYPE_OVER_LIMIT: t("REPORT_LABEL_OVER_LIMIT", lang=lang),
    }
    return label_map.get(report_type, t("REPORT_MENU_TITLE", lang=lang))


def _build_report_date_keyboard(report_type: str, lang: str = "en") -> InlineKeyboardMarkup:
    today = _today_local_date()
    dates = [today - timedelta(days=i) for i in range(7)]
    keyboard: list[list[InlineKeyboardButton]] = []

    first = dates[0]
    keyboard.append([
        InlineKeyboardButton(
            t("BTN_TODAY", lang=lang, date=first.strftime("%d/%m")),
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

    keyboard.append([InlineKeyboardButton(t("BTN_BACK", lang=lang), callback_data=REPORT_CALLBACK_BACK_TO_MENU)])
    return InlineKeyboardMarkup(keyboard)


def _build_report_action_keyboard(report_type: str, target_date: str, lang: str = "en") -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(t("BTN_EXPORT_HTML", lang=lang), callback_data=f"{REPORT_CALLBACK_EXPORT_PREFIX}{report_type}:{target_date}")],
        [InlineKeyboardButton(t("BTN_CHANGE_DATE", lang=lang), callback_data=f"{REPORT_CALLBACK_TYPE_PREFIX}{report_type}")],
        [InlineKeyboardButton(t("BTN_BACK", lang=lang), callback_data=REPORT_CALLBACK_BACK_TO_MENU)],
    ]
    return InlineKeyboardMarkup(keyboard)


def _build_coming_soon_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton(t("BTN_BACK", lang=lang), callback_data=REPORT_CALLBACK_BACK_TO_MENU)]])


def _report_filename(report_type: str, target_date: str, lang: str = "en") -> tuple[str, str]:
    if report_type == REPORT_TYPE_TRANSACTION:
        return (
            f"transaction_report_{target_date}.html",
            f"{t('REPORT_LABEL_TRANSACTION', lang=lang)}_{target_date}.html",
        )
    if report_type == REPORT_TYPE_NUMBER_DETAIL:
        return (
            f"number_detail_report_{target_date}.html",
            f"{t('REPORT_LABEL_NUMBER_DETAIL', lang=lang)}_{target_date}.html",
        )
    if report_type == REPORT_TYPE_SETTLEMENT:
        return (
            f"settlement_report_{target_date}.html",
            f"{t('REPORT_LABEL_SETTLEMENT', lang=lang)}_{target_date}.html",
        )
    if report_type == REPORT_TYPE_OVER_LIMIT:
        return (
            f"over_limit_report_{target_date}.html",
            f"{t('REPORT_LABEL_OVER_LIMIT', lang=lang)}_{target_date}.html",
        )
    return (
        f"report_{report_type}_{target_date}.html",
        f"{t('REPORT_MENU_TITLE', lang=lang)}_{target_date}.html",
    )


def _generate_report_text(report_type: str, target_date: str, lang: str = "en") -> str | None:
    """Generate report text for a given type and date. Returns None for unknown types."""
    if report_type == REPORT_TYPE_TRANSACTION:
        report_data = transaction_report_service.generate_report(target_date)
        return format_transaction_report(report_data, lang=lang)
    if report_type == REPORT_TYPE_NUMBER_DETAIL:
        report_data = number_detail_report_service.generate_report(target_date)
        return format_number_detail_report(report_data, lang=lang)
    if report_type == REPORT_TYPE_SETTLEMENT:
        current_rate = ReportNormalizer.to_decimal(admin_settings_service.get_agent_commission_rate())
        report_data = settlement_report_service.generate_report(target_date=target_date, agent_commission_rate=current_rate)
        return format_settlement_report_telegram(report_data, lang=lang)
    if report_type == REPORT_TYPE_OVER_LIMIT:
        report_data = over_limit_report_service.generate(target_date)
        return format_over_limit_report(report_data)
    return None

# =========================================================
# Admin helpers
# =========================================================
def _build_admin_menu_text(lang: str = "en") -> str:
    return t("BTN_ADMIN", lang=lang)


def _build_admin_menu_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(f"1. {t('ADMIN_AGENT_COMM_SETTING', lang=lang)}", callback_data=CALLBACK_ADMIN_AGENT_MENU)],
        [InlineKeyboardButton(f"2. {t('ADMIN_BONUS_PAYOUT_SETTING', lang=lang)}", callback_data=CALLBACK_ADMIN_BONUS_MENU)],
        [InlineKeyboardButton(f"3. {t('ADMIN_OVER_LIMIT_SETTING', lang=lang)}", callback_data=CALLBACK_ADMIN_LIMIT_MENU)],
        [InlineKeyboardButton(f"4. {t('ADMIN_NOTIFICATIONS', lang=lang)}", callback_data=CALLBACK_ADMIN_NOTIFICATIONS_MENU)],
        [InlineKeyboardButton(f"5. {t('ADMIN_BET_TIME_LIMIT', lang=lang)}", callback_data=CALLBACK_ADMIN_TIME_LIMIT_MENU)],
        [InlineKeyboardButton(f"6. {t('ADMIN_SYSTEM_TIME_ZONE', lang=lang)}", callback_data=CALLBACK_ADMIN_SYSTEM_TZ_MENU)],
        [InlineKeyboardButton(f"7. {t('ADMIN_SET_ADMIN', lang=lang)}", callback_data=CALLBACK_ADMIN_SET_ADMIN)],
        [InlineKeyboardButton(t("BTN_CLOSE", lang=lang), callback_data=CALLBACK_ADMIN_CLOSE)],
    ]
    return InlineKeyboardMarkup(keyboard)


def _build_admin_menu_kb(lang: str = "en") -> ReplyKeyboardMarkup:
    """ReplyKeyboard for admin menu (top-level)."""
    return ReplyKeyboardMarkup(
        [[KeyboardButton(f"1. {t('ADMIN_AGENT_COMM_SETTING', lang=lang)}"), KeyboardButton(f"2. {t('ADMIN_BONUS_PAYOUT_SETTING', lang=lang)}")],
         [KeyboardButton(f"3. {t('ADMIN_OVER_LIMIT_SETTING', lang=lang)}"), KeyboardButton(f"4. {t('ADMIN_NOTIFICATIONS', lang=lang)}")],
         [KeyboardButton(f"5. {t('ADMIN_BET_TIME_LIMIT', lang=lang)}"), KeyboardButton(f"6. {t('ADMIN_SYSTEM_TIME_ZONE', lang=lang)}")],
         [KeyboardButton(f"7. {t('ADMIN_SET_ADMIN', lang=lang)}"), KeyboardButton(t("BTN_BACK", lang=lang))]],
        resize_keyboard=True,
    )


def _build_set_admin_text(lang: str = "en") -> str:
    return f"👑 {t('ADMIN_SET_ADMIN', lang=lang)}\n\n{t('PROMPT_SELECT_ADMIN_OPTION', lang=lang)}"


def _build_set_admin_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(t("ADMIN_VIEW_ADMIN_LIST", lang=lang), callback_data=CALLBACK_ADMIN_VIEW_ADMINS)],
        [InlineKeyboardButton(t("ADMIN_ADD_ADMIN", lang=lang), callback_data=CALLBACK_ADMIN_ADD_ADMIN)],
        [InlineKeyboardButton(t("ADMIN_REMOVE_ADMIN", lang=lang), callback_data=CALLBACK_ADMIN_REMOVE_ADMIN)],
        [InlineKeyboardButton(t("BTN_BACK", lang=lang), callback_data=CALLBACK_ADMIN_BACK)],
    ]
    return InlineKeyboardMarkup(keyboard)


def _build_agent_comm_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(t("ADMIN_VIEW_CURRENT_AGENT_COMM", lang=lang), callback_data=CALLBACK_ADMIN_AGENT_VIEW)],
        [InlineKeyboardButton(t("ADMIN_EDIT_AGENT_COMM", lang=lang), callback_data=CALLBACK_ADMIN_AGENT_EDIT)],
        [InlineKeyboardButton(t("BTN_BACK", lang=lang), callback_data=CALLBACK_ADMIN_BACK)],
    ]
    return InlineKeyboardMarkup(keyboard)


def _build_bonus_payout_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(t("ADMIN_VIEW_CURRENT_BONUS_PAYOUT", lang=lang), callback_data=CALLBACK_ADMIN_BONUS_VIEW)],
        [InlineKeyboardButton(t("ADMIN_EDIT_BONUS_PAYOUT", lang=lang), callback_data=CALLBACK_ADMIN_BONUS_EDIT)],
        [InlineKeyboardButton(t("BTN_BACK", lang=lang), callback_data=CALLBACK_ADMIN_BACK)],
    ]
    return InlineKeyboardMarkup(keyboard)


def _build_over_limit_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(t("ADMIN_VIEW_CURRENT_OVER_LIMIT", lang=lang), callback_data=CALLBACK_ADMIN_LIMIT_VIEW)],
        [InlineKeyboardButton(t("ADMIN_EDIT_OVER_LIMIT", lang=lang), callback_data=CALLBACK_ADMIN_LIMIT_EDIT)],
        [InlineKeyboardButton(t("ADMIN_SET_OVER_LIMIT_ACTION", lang=lang), callback_data=CALLBACK_ADMIN_LIMIT_ACTION_MENU)],
        [InlineKeyboardButton(t("BTN_BACK", lang=lang), callback_data=CALLBACK_ADMIN_BACK)],
    ]
    return InlineKeyboardMarkup(keyboard)


def _build_over_limit_action_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(t("ADMIN_CONTINUE_ACCEPTING", lang=lang), callback_data=CALLBACK_ADMIN_LIMIT_ACTION_ACCEPT)],
        [InlineKeyboardButton(t("ADMIN_REJECT_BET", lang=lang), callback_data=CALLBACK_ADMIN_LIMIT_ACTION_REJECT)],
        [InlineKeyboardButton(t("BTN_BACK", lang=lang), callback_data=CALLBACK_ADMIN_LIMIT_MENU)],
    ]
    return InlineKeyboardMarkup(keyboard)


def _build_notifications_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(t("ADMIN_VIEW_CURRENT_NOTIFICATION_SETTINGS", lang=lang), callback_data=CALLBACK_ADMIN_NOTIFICATIONS_VIEW)],
        [
            InlineKeyboardButton(t("ADMIN_ON", lang=lang), callback_data=CALLBACK_ADMIN_NOTIFICATIONS_ON),
            InlineKeyboardButton(t("ADMIN_OFF", lang=lang), callback_data=CALLBACK_ADMIN_NOTIFICATIONS_OFF),
        ],
        [InlineKeyboardButton(t("BTN_BACK", lang=lang), callback_data=CALLBACK_ADMIN_BACK)],
    ]
    return InlineKeyboardMarkup(keyboard)


def _build_time_limit_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(t("ADMIN_VIEW_CURRENT_CUTOFF_TIME", lang=lang), callback_data=CALLBACK_ADMIN_TIME_LIMIT_VIEW)],
        [InlineKeyboardButton(t("ADMIN_EDIT_CUTOFF_TIME", lang=lang), callback_data=CALLBACK_ADMIN_TIME_LIMIT_EDIT)],
        [InlineKeyboardButton(t("BTN_BACK", lang=lang), callback_data=CALLBACK_ADMIN_BACK)],
    ]
    return InlineKeyboardMarkup(keyboard)


def _build_system_timezone_keyboard(lang: str = "en") -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(t("ADMIN_VIEW_CURRENT_TIME_ZONE", lang=lang), callback_data=CALLBACK_ADMIN_SYSTEM_TZ_VIEW)],
        [
            InlineKeyboardButton(t("ADMIN_TIMEZONE_KL", lang=lang), callback_data=CALLBACK_ADMIN_SYSTEM_TZ_KL),
            InlineKeyboardButton(t("ADMIN_TIMEZONE_HCM", lang=lang), callback_data=CALLBACK_ADMIN_SYSTEM_TZ_HCM),
        ],
        [InlineKeyboardButton(t("BTN_BACK", lang=lang), callback_data=CALLBACK_ADMIN_BACK)],
    ]
    return InlineKeyboardMarkup(keyboard)


def _format_admin_list_text(lang: str = "en") -> str:
    admins = admin_auth_service.list_admins()
    if not admins:
        return f"👑 {t('ADMIN_VIEW_ADMIN_LIST', lang=lang)}\n\n{t('REPORT_NO_DATA', lang=lang)}"
    lines = [f"👑 {t('ADMIN_VIEW_ADMIN_LIST', lang=lang)}", ""]
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

    user_id = update.effective_user.id if update.effective_user else None
    target_date = _today_iso()
    current_rate = ReportNormalizer.to_decimal(admin_settings_service.get_agent_commission_rate())
    report_data = settlement_report_service.generate_report(
        target_date=target_date,
        agent_commission_rate=current_rate,
    )
    text = format_settlement_report_telegram(report_data, lang=_get_user_lang(user_id))
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
    await _clear_transient_messages(update, context)
    await _send_status_message(update, context, _build_env_region_message(user_id, "MN"), reply_markup=ReplyKeyboardRemove())


async def mt_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.effective_user:
        return
    user_id = update.effective_user.id
    _set_user_target_date(user_id, _today_iso())
    _set_user_region(user_id, "MT")
    await _clear_transient_messages(update, context)
    await _send_status_message(update, context, _build_env_region_message(user_id, "MT"), reply_markup=ReplyKeyboardRemove())


async def mb_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.effective_user:
        return
    user_id = update.effective_user.id
    _set_user_target_date(user_id, _today_iso())
    _set_user_region(user_id, "MB")
    await _clear_transient_messages(update, context)
    await _send_status_message(update, context, _build_env_region_message(user_id, "MB"), reply_markup=ReplyKeyboardRemove())


async def myid_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.effective_user:
        return
    await _clear_menu_message(update, context)
    await update.message.reply_text(f"Your Telegram user_id: {update.effective_user.id}", reply_markup=ReplyKeyboardRemove())


async def lang_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.effective_user:
        return
    user_id = update.effective_user.id
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🇬🇧 English", callback_data=f"{CALLBACK_LANG_SET_PREFIX}en"),
            InlineKeyboardButton("🇨🇳 中文", callback_data=f"{CALLBACK_LANG_SET_PREFIX}zh"),
            InlineKeyboardButton("🇻🇳 Tiếng Việt", callback_data=f"{CALLBACK_LANG_SET_PREFIX}vi"),
        ]
    ])
    await update.message.reply_text(t("LANG_SELECT_PROMPT", _get_user_lang(user_id)), reply_markup=keyboard)


async def handle_lang_select(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.from_user:
        return
    await query.answer()
    user_id = query.from_user.id
    lang_code = query.data.replace(CALLBACK_LANG_SET_PREFIX, "", 1)
    if lang_code not in {"en", "zh", "vi"}:
        return
    _set_user_lang(user_id, lang_code)
    register_chat_commands = context.application.bot_data.get("register_chat_commands")
    if callable(register_chat_commands) and query.message:
        try:
            await register_chat_commands(query.message.chat_id, lang_code)
        except Exception as exc:
            log_step(f"? Failed to refresh command menu for chat {query.message.chat_id}: {exc}")
    key_map = {"en": "LANG_SET_EN", "zh": "LANG_SET_ZH", "vi": "LANG_SET_VI"}
    await query.edit_message_text(text=t(key_map[lang_code], lang_code))


async def delete_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.effective_user:
        return
    user_id = update.effective_user.id
    args = context.args or []
    if len(args) < 1:
        await update.message.reply_text(t("ADMIN_USAGE_DELETE_SLASH", _get_user_lang(user_id)))
        return
    ticket_no = str(args[0]).upper()
    target_date = _get_user_target_date(user_id)
    _, response_text = delete_ticket(ticket_no, target_date, lang=_get_user_lang(user_id))
    await _clear_menu_message(update, context)
    await update.message.reply_text(_as_monospace_html(_build_delete_success_message(response_text)), parse_mode="HTML", reply_markup=ReplyKeyboardRemove())


async def handle_bot_joined_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send welcome message with main keyboard when bot is added to a group."""
    if not update.my_chat_member:
        return
    new_status = update.my_chat_member.new_chat_member.status
    old_status = update.my_chat_member.old_chat_member.status
    # Only fire when transitioning INTO member/administrator
    if new_status not in ("member", "administrator"):
        return
    if old_status in ("member", "administrator"):
        return
    chat_id = update.my_chat_member.chat.id
    await context.bot.send_message(
        chat_id=chat_id,
        text="👋 M33 Lotto Bot is ready! Use /start to open the menu.",
        reply_markup=get_main_menu_keyboard(lang="en"),
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.effective_user:
        return
    user_id = update.effective_user.id
    _set_user_state(user_id, UserState.IDLE)
    register_chat_commands = context.application.bot_data.get("register_chat_commands")
    if callable(register_chat_commands) and update.effective_chat:
        try:
            await register_chat_commands(update.effective_chat.id, _get_user_lang(user_id))
        except Exception as exc:
            log_step(f"? Failed to sync command menu for chat {update.effective_chat.id}: {exc}")
    await show_main_menu(update, context)


# =========================================================
# Menus
# =========================================================
async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.effective_user:
        return
    user_id = update.effective_user.id
    _set_user_state(user_id, UserState.IDLE)
    await _clear_transient_messages(update, context)
    await _send_menu_message(update, context, _menu_anchor_text(), _build_main_menu_kb(user_id))


async def show_bet_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.effective_user:
        return
    user_id = update.effective_user.id
    reply_markup = get_bet_menu_keyboard()
    await _send_menu_message(update, context, t("BTN_BET", _get_user_lang(user_id)), reply_markup)


async def main_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # 清理用户状态，确保没有旧信息遗留
    user_id = update.effective_user.id
    await _clear_transient_messages(update, context)
    _set_user_state(user_id, UserState.IDLE)
    if not update.message or not update.effective_user:
        return
    text = update.message.text
    user_id = update.effective_user.id
    _ensure_user_context(user_id)
    lang = _get_user_lang(user_id)

    if text == t("BTN_BET", lang):
        _set_user_state(user_id, UserState.BET_REGION)
        _set_user_target_date(user_id, _today_iso())
        await _send_menu_message(update, context, t("PROMPT_SELECT_REGION", lang), _build_region_kb(lang=lang))
    elif text == t("BTN_REPORT", lang):
        _set_user_state(user_id, UserState.REPORT_TYPE)
        await _send_status_message(update, context, t("PROMPT_SELECT_REPORT_TYPE", lang), reply_markup=_build_report_type_kb(lang=lang))
    elif text == t("BTN_RESULT", lang):
        _set_user_state(user_id, UserState.RESULT_DATE)
        await _send_status_message(update, context, _build_result_menu_text(user_id), reply_markup=_build_result_date_kb(lang=lang))
    elif text == t("BTN_OTHER_DAY_INPUT", lang):
        _set_user_state(user_id, UserState.ODI_DATE)
        await _send_status_message(update, context, t("PROMPT_SELECT_DATE", lang), reply_markup=_build_odi_kb(lang=lang))
    elif text == t("BTN_ADMIN", lang):
        if not admin_auth_service.is_admin(user_id):
            await update.message.reply_text(t("PROMPT_ACCESS_DENIED", lang))
            return
        _set_user_state(user_id, UserState.ADMIN_MENU)
        await _send_status_message(update, context, _build_admin_menu_text(lang=lang), reply_markup=_build_admin_menu_kb(lang=lang))
    elif text == t("BTN_INFO", lang):
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
        await _clear_transient_messages(update, context)
        await _send_status_message(update, context, _build_env_region_message(user_id, region), reply_markup=ReplyKeyboardRemove())
    else:
        await update.message.reply_text(t("PROMPT_INVALID_REGION", _get_user_lang(user_id)))


# =========================================================
# Report UI
# =========================================================
async def handle_report_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query:
        return
    await query.answer()
    user_id = query.from_user.id if query.from_user else None
    lang = _get_user_lang(user_id)
    await query.edit_message_text(text=t("REPORT_MENU_TITLE", lang=lang), reply_markup=_build_report_menu_keyboard(lang=lang))


async def handle_report_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query:
        return
    await query.answer()
    report_type = query.data.replace(REPORT_CALLBACK_TYPE_PREFIX, "", 1)
    user_id = query.from_user.id if query.from_user else None
    lang = _get_user_lang(user_id)
    await query.edit_message_text(text=_build_report_date_text(report_type, lang=lang), reply_markup=_build_report_date_keyboard(report_type, lang=lang))


async def handle_report_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query:
        return
    await query.answer()
    user_id = query.from_user.id if query.from_user else None
    payload = query.data.replace(REPORT_CALLBACK_DATE_PREFIX, "", 1)
    try:
        report_type, target_date = payload.split(":")
    except ValueError:
        await query.edit_message_text(t("PROMPT_INVALID_REPORT"))
        return

    if report_type == REPORT_TYPE_TRANSACTION:
        report_data = transaction_report_service.generate_report(target_date)
        text = format_transaction_report(report_data, lang=_get_user_lang(user_id))
    elif report_type == REPORT_TYPE_NUMBER_DETAIL:
        report_data = number_detail_report_service.generate_report(target_date)
        text = format_number_detail_report(report_data, lang=_get_user_lang(user_id))
    elif report_type == REPORT_TYPE_SETTLEMENT:
        current_rate = ReportNormalizer.to_decimal(admin_settings_service.get_agent_commission_rate())
        report_data = settlement_report_service.generate_report(target_date=target_date, agent_commission_rate=current_rate)
        text = format_settlement_report_telegram(report_data, lang=_get_user_lang(user_id))
    elif report_type == REPORT_TYPE_OVER_LIMIT:
        report_data = over_limit_report_service.generate(target_date)
        text = format_over_limit_report(report_data)
    else:
        await query.edit_message_text(text=t("REPORT_COMING_SOON", lang=_get_user_lang(user_id)), reply_markup=_build_coming_soon_keyboard(lang=_get_user_lang(user_id)))
        return

    await query.edit_message_text(text=_as_monospace_html(text), reply_markup=_build_report_action_keyboard(report_type, target_date, lang=_get_user_lang(user_id)), parse_mode="HTML")


async def handle_report_export(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query:
        return
    await query.answer()
    payload = query.data.replace(REPORT_CALLBACK_EXPORT_PREFIX, "", 1)
    try:
        report_type, target_date = payload.split(":")
    except ValueError:
        await query.edit_message_text(t("PROMPT_INVALID_EXPORT"))
        return

    user_id = query.from_user.id if query.from_user else None
    lang = _get_user_lang(user_id)

    if report_type == REPORT_TYPE_TRANSACTION:
        report_data = transaction_report_service.generate_report(target_date)
        html = build_transaction_report_html(report_data, lang=lang)
    elif report_type == REPORT_TYPE_NUMBER_DETAIL:
        report_data = number_detail_report_service.generate_report(target_date)
        html = build_number_detail_report_html(report_data, lang=lang)
    elif report_type == REPORT_TYPE_SETTLEMENT:
        current_rate = ReportNormalizer.to_decimal(admin_settings_service.get_agent_commission_rate())
        report_data = settlement_report_service.generate_report(target_date=target_date, agent_commission_rate=current_rate)
        html = export_settlement_report_html(report_data, lang=lang)
    elif report_type == REPORT_TYPE_OVER_LIMIT:
        report_data = over_limit_report_service.generate(target_date)
        html = export_over_limit_report_html(report_data, lang=lang)
    else:
        await query.answer(t("PROMPT_EXPORT_UNAVAILABLE", lang=lang), show_alert=True)
        return

    storage_filename, display_filename = _report_filename(report_type, target_date, lang=lang)
    output_path = Path("data") / storage_filename
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")

    if query.message:
        with output_path.open("rb") as f:
            await query.message.reply_document(document=f, filename=display_filename)


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
            await query.edit_message_text(t("PROMPT_CLOSED"))
        except Exception:
            pass


# =========================================================
# Admin UI
# =========================================================
async def handle_admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.from_user:
        return
    user_id = query.from_user.id
    lang = _get_user_lang(user_id)
    await query.answer()
    if not admin_auth_service.is_admin(user_id):
        await query.edit_message_text(t("PROMPT_ACCESS_DENIED", lang))
        return
    await query.edit_message_text(text=_build_admin_menu_text(lang=lang), reply_markup=_build_admin_menu_keyboard(lang=lang))


async def handle_admin_set_admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.from_user:
        return
    user_id = query.from_user.id
    lang = _get_user_lang(user_id)
    await query.answer()
    if not admin_auth_service.is_admin(user_id):
        await query.edit_message_text(t("PROMPT_ACCESS_DENIED", lang))
        return
    await query.edit_message_text(text=_build_set_admin_text(lang=lang), reply_markup=_build_set_admin_keyboard(lang=lang))


async def handle_admin_view_admins(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.from_user:
        return
    user_id = query.from_user.id
    lang = _get_user_lang(user_id)
    await query.answer()
    if not admin_auth_service.is_admin(user_id):
        await query.edit_message_text(t("PROMPT_ACCESS_DENIED", lang))
        return
    await query.edit_message_text(text=_format_admin_list_text(lang=lang), reply_markup=_build_set_admin_keyboard(lang=lang))


async def handle_admin_add_admin_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.from_user:
        return
    user_id = query.from_user.id
    lang = _get_user_lang(user_id)
    await query.answer()
    if not admin_auth_service.is_admin(user_id):
        await query.edit_message_text(t("PROMPT_ACCESS_DENIED", lang))
        return
    _set_admin_waiting_action(user_id, "ADD_ADMIN")
    await query.edit_message_text(
        text=t("ADMIN_PROMPT_ADD_ADMIN", lang=lang),
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(t("BTN_BACK", lang=lang), callback_data=CALLBACK_ADMIN_SET_ADMIN)]]),
    )


async def handle_admin_remove_admin_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.from_user:
        return
    user_id = query.from_user.id
    lang = _get_user_lang(user_id)
    await query.answer()
    if not admin_auth_service.is_admin(user_id):
        await query.edit_message_text(t("PROMPT_ACCESS_DENIED", lang))
        return
    _set_admin_waiting_action(user_id, "REMOVE_ADMIN")
    await query.edit_message_text(
        text=t("ADMIN_PROMPT_REMOVE_ADMIN", lang=lang),
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(t("BTN_BACK", lang=lang), callback_data=CALLBACK_ADMIN_SET_ADMIN)]]),
    )


async def handle_admin_agent_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.from_user:
        return
    user_id = query.from_user.id
    lang = _get_user_lang(user_id)
    await query.answer()
    await query.edit_message_text(text=t("ADMIN_AGENT_COMM_SETTING", lang), reply_markup=_build_agent_comm_keyboard(lang=lang))


async def handle_admin_agent_view(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.from_user:
        return
    user_id = query.from_user.id
    lang = _get_user_lang(user_id)
    await query.answer()
    rate = admin_settings_service.get_agent_commission_rate()
    await query.edit_message_text(text=t("ADMIN_AGENT_COMM_CURRENT", lang, rate=rate), reply_markup=_build_agent_comm_keyboard(lang=lang))


async def handle_admin_agent_edit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.from_user:
        return
    user_id = query.from_user.id
    lang = _get_user_lang(user_id)
    await query.answer()
    _set_admin_waiting_action(user_id, "SET_AGENT_COMM")
    await query.edit_message_text(
        text=t("ADMIN_ENTER_COMMISSION_RATE", lang),
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(t("BTN_BACK", lang=lang), callback_data=CALLBACK_ADMIN_AGENT_MENU)]]),
    )


async def handle_admin_bonus_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.from_user:
        return
    user_id = query.from_user.id
    lang = _get_user_lang(user_id)
    await query.answer()
    await query.edit_message_text(text=t("ADMIN_BONUS_PAYOUT_SETTING", lang), reply_markup=_build_bonus_payout_keyboard(lang=lang))


async def handle_admin_bonus_view(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.from_user:
        return
    user_id = query.from_user.id
    lang = _get_user_lang(user_id)
    await query.answer()
    await query.edit_message_text(text=admin_settings_service.format_bonus_payout_text(lang=lang), reply_markup=_build_bonus_payout_keyboard(lang=lang))


async def handle_admin_bonus_edit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.from_user:
        return
    await query.answer()
    user_id = query.from_user.id
    lang = _get_user_lang(user_id)
    _set_admin_waiting_action(user_id, "SET_BONUS_PAYOUT_BULK")
    template = admin_settings_service.build_bonus_edit_template()
    await query.edit_message_text(
        text=f"{t('ADMIN_EDIT_BONUS_PAYOUT', lang=lang)}\n\n{template}",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(t("BTN_BACK", lang=lang), callback_data=CALLBACK_ADMIN_BONUS_MENU)]]),
    )


async def handle_admin_limit_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.from_user:
        return
    user_id = query.from_user.id
    lang = _get_user_lang(user_id)
    await query.answer()
    await query.edit_message_text(text=t("ADMIN_OVER_LIMIT_SETTING", lang), reply_markup=_build_over_limit_keyboard(lang=lang))


async def handle_admin_limit_view(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.from_user:
        return
    user_id = query.from_user.id
    lang = _get_user_lang(user_id)
    await query.answer()
    await query.edit_message_text(text=admin_settings_service.format_limit_text(lang=lang), reply_markup=_build_over_limit_keyboard(lang=lang))


async def handle_admin_limit_edit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.from_user:
        return
    await query.answer()
    user_id = query.from_user.id
    lang = _get_user_lang(user_id)
    _set_admin_waiting_action(user_id, "SET_OVER_LIMIT_BULK")
    template = admin_settings_service.build_limit_edit_template()
    await query.edit_message_text(
        text=f"{t('ADMIN_EDIT_OVER_LIMIT', lang=lang)}\n\n{template}",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(t("BTN_BACK", lang=lang), callback_data=CALLBACK_ADMIN_LIMIT_MENU)]]),
    )


async def handle_admin_limit_action_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.from_user:
        return
    user_id = query.from_user.id
    lang = _get_user_lang(user_id)
    await query.answer()
    current_action = admin_settings_service.get_over_limit_action()
    await query.edit_message_text(text=t("ADMIN_OVER_LIMIT_CURRENT", lang, action=current_action), reply_markup=_build_over_limit_action_keyboard(lang=lang))


async def handle_admin_limit_action_accept(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query:
        return
    await query.answer()
    user_id = query.from_user.id if query.from_user else None
    lang = _get_user_lang(user_id)
    admin_settings_service.set_over_limit_action("ACCEPT")
    await query.edit_message_text(text=t("ADMIN_OVER_LIMIT_SET_ACCEPT", lang), reply_markup=_build_over_limit_action_keyboard(lang=lang))


async def handle_admin_limit_action_reject(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query:
        return
    await query.answer()
    user_id = query.from_user.id if query.from_user else None
    lang = _get_user_lang(user_id)
    admin_settings_service.set_over_limit_action("REJECT")
    await query.edit_message_text(text=t("ADMIN_OVER_LIMIT_SET_REJECT", lang), reply_markup=_build_over_limit_action_keyboard(lang=lang))


async def handle_admin_notifications_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.from_user:
        return
    user_id = query.from_user.id
    await query.answer()
    await query.edit_message_text(text=t("ADMIN_NOTIFICATIONS", _get_user_lang(user_id)), reply_markup=_build_notifications_keyboard())


async def handle_admin_notifications_view(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.from_user:
        return
    user_id = query.from_user.id
    await query.answer()
    await query.edit_message_text(text=admin_settings_service.format_notification_text(lang=_get_user_lang(user_id)), reply_markup=_build_notifications_keyboard())


async def handle_admin_notifications_on(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.from_user:
        return
    user_id = query.from_user.id
    await query.answer()
    admin_settings_service.set_customer_notification_enabled(True)
    await query.edit_message_text(text=t("ADMIN_NOTIF_SET_ON", _get_user_lang(user_id)), reply_markup=_build_notifications_keyboard())


async def handle_admin_notifications_off(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.from_user:
        return
    user_id = query.from_user.id
    await query.answer()
    admin_settings_service.set_customer_notification_enabled(False)
    await query.edit_message_text(text=t("ADMIN_NOTIF_SET_OFF", _get_user_lang(user_id)), reply_markup=_build_notifications_keyboard())


async def handle_admin_time_limit_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.from_user:
        return
    user_id = query.from_user.id
    await query.answer()
    await query.edit_message_text(text=t("ADMIN_BET_TIME_LIMIT", _get_user_lang(user_id)), reply_markup=_build_time_limit_keyboard())


async def handle_admin_time_limit_view(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.from_user:
        return
    user_id = query.from_user.id
    await query.answer()
    await query.edit_message_text(text=admin_settings_service.format_cutoff_time_text(lang=_get_user_lang(user_id)), reply_markup=_build_time_limit_keyboard())


async def handle_admin_time_limit_edit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.from_user:
        return
    await query.answer()
    user_id = query.from_user.id
    lang = _get_user_lang(user_id)
    _set_admin_waiting_action(user_id, "SET_CUTOFF_TIME_BULK")
    template = admin_settings_service.build_cutoff_time_edit_template()
    await query.edit_message_text(
        text=f"{t('ADMIN_EDIT_CUTOFF_TIME', lang=lang)}\n\n{template}",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(t("BTN_BACK", lang=lang), callback_data=CALLBACK_ADMIN_TIME_LIMIT_MENU)]]),
    )


async def handle_admin_system_tz_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.from_user:
        return
    user_id = query.from_user.id
    await query.answer()
    await query.edit_message_text(text=t("ADMIN_SYSTEM_TIME_ZONE", _get_user_lang(user_id)), reply_markup=_build_system_timezone_keyboard())


async def handle_admin_system_tz_view(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.from_user:
        return
    user_id = query.from_user.id
    await query.answer()
    await query.edit_message_text(text=admin_settings_service.format_system_timezone_text(lang=_get_user_lang(user_id)), reply_markup=_build_system_timezone_keyboard())


async def handle_admin_system_tz_kl(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.from_user:
        return
    user_id = query.from_user.id
    await query.answer()
    admin_settings_service.set_system_timezone_name("Asia/Kuala_Lumpur")
    await query.edit_message_text(text=t("ADMIN_TIMEZONE_SET_KL", _get_user_lang(user_id)), reply_markup=_build_system_timezone_keyboard())


async def handle_admin_system_tz_hcm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.from_user:
        return
    user_id = query.from_user.id
    await query.answer()
    admin_settings_service.set_system_timezone_name("Asia/Ho_Chi_Minh")
    await query.edit_message_text(text=t("ADMIN_TIMEZONE_SET_HCM", _get_user_lang(user_id)), reply_markup=_build_system_timezone_keyboard())


async def handle_admin_back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.from_user:
        return
    user_id = query.from_user.id
    await query.answer()
    if not admin_auth_service.is_admin(user_id):
        await query.edit_message_text(t("PROMPT_ACCESS_DENIED", _get_user_lang(user_id)))
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
            await query.edit_message_text(t("PROMPT_CLOSED"))
        except Exception:
            pass


# =========================================================
# Other Day UI
# =========================================================
def _build_other_day_menu_text(user_id: int) -> str:
    return t("BTN_OTHER_DAY_INPUT", _get_user_lang(user_id))


def _build_other_day_keyboard() -> InlineKeyboardMarkup:
    today = _today_local_date()
    prev_dates = [today - timedelta(days=i) for i in range(3, 0, -1)]
    next_dates = [today + timedelta(days=i) for i in range(1, 4)]
    keyboard = [
        [InlineKeyboardButton(d.strftime("%d/%m"), callback_data=f"{CALLBACK_ODI_DATE_PREFIX}{d.isoformat()}") for d in prev_dates],
        [InlineKeyboardButton(t("BTN_TODAY", date=today.strftime("%d/%m")), callback_data=CALLBACK_ODI_SET_TODAY)],
        [InlineKeyboardButton(d.strftime("%d/%m"), callback_data=f"{CALLBACK_ODI_DATE_PREFIX}{d.isoformat()}") for d in next_dates],
        [InlineKeyboardButton(t("BTN_SET_CUSTOM_DATE"), callback_data=CALLBACK_ODI_SET_CUSTOM)],
        [InlineKeyboardButton(t("BTN_CLOSE"), callback_data=CALLBACK_ODI_CLOSE)],
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
    await query.edit_message_text(text=t("MENU_OTHER_DAY_INPUT", _get_user_lang(user_id)))
    if query.message:
        await query.message.reply_text(t("MENU_BET", _get_user_lang(user_id)), reply_markup=get_bet_menu_keyboard())


async def handle_other_day_set_today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query or not query.from_user:
        return
    user_id = query.from_user.id
    _ensure_user_context(user_id)
    await query.answer()
    _set_user_target_date(user_id, _today_iso())
    await query.edit_message_text(text=t("MENU_OTHER_DAY_INPUT", _get_user_lang(user_id)))
    if query.message:
        await query.message.reply_text(t("MENU_BET", _get_user_lang(user_id)), reply_markup=get_bet_menu_keyboard())


async def handle_other_day_set_custom(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query or not query.from_user:
        return
    user_id = query.from_user.id
    _ensure_user_context(user_id)
    await query.answer()
    _set_waiting_custom_date(user_id, True)
    await query.edit_message_text(text=t("PROMPT_CUSTOM_DATE", _get_user_lang(user_id)))


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
            await query.edit_message_text(t("PROMPT_CLOSED"))
        except Exception:
            pass


# =========================================================
# Result UI
# =========================================================
def _build_result_menu_text(user_id: int | None = None) -> str:
    return t("BTN_RESULT", _get_user_lang(user_id))


def _build_result_region_text(draw_date: str, user_id: int | None = None) -> str:
    return t("BTN_RESULT", _get_user_lang(user_id))


def _build_result_date_kb(lang: str = "en") -> ReplyKeyboardMarkup:
    """ReplyKeyboard for result date selection (RESULT_DATE)."""
    today = _today_local_date()
    dates = [today - timedelta(days=i) for i in range(7)]
    row1 = [KeyboardButton(t("BTN_TODAY", lang=lang, date=dates[0].strftime("%d/%m")))]
    row2 = [KeyboardButton(d.strftime("%d/%m")) for d in dates[1:3]]
    row3 = [KeyboardButton(d.strftime("%d/%m")) for d in dates[3:5]]
    row4 = [KeyboardButton(d.strftime("%d/%m")) for d in dates[5:7]]
    return ReplyKeyboardMarkup(
        [row1, row2, row3, row4, [KeyboardButton(t("BTN_BACK", lang=lang))]],
        resize_keyboard=True,
    )


def _build_result_region_kb(lang: str = "en") -> ReplyKeyboardMarkup:
    """ReplyKeyboard for result region selection (RESULT_REGION)."""
    return ReplyKeyboardMarkup(
        [[KeyboardButton("MN"), KeyboardButton("MT"), KeyboardButton("MB")],
         [KeyboardButton(t("BTN_BACK", lang=lang))]],
        resize_keyboard=True,
    )


def _build_result_date_keyboard() -> InlineKeyboardMarkup:
    today = _today_local_date()
    dates = [today - timedelta(days=i) for i in range(7)]
    keyboard = []
    first = dates[0]
    keyboard.append([InlineKeyboardButton(t("BTN_TODAY", date=first.strftime("%d/%m")), callback_data=f"{CALLBACK_RESULT_DATE_PREFIX}{first.isoformat()}")])
    row = []
    for d in dates[1:]:
        row.append(InlineKeyboardButton(d.strftime("%d/%m"), callback_data=f"{CALLBACK_RESULT_DATE_PREFIX}{d.isoformat()}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton(t("BTN_BACK"), callback_data=CALLBACK_RESULT_CLOSE)])
    return InlineKeyboardMarkup(keyboard)


def _build_result_region_keyboard(draw_date: str) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("MN", callback_data=f"{CALLBACK_RESULT_VIEW_PREFIX}{draw_date}:MN"),
            InlineKeyboardButton("MT", callback_data=f"{CALLBACK_RESULT_VIEW_PREFIX}{draw_date}:MT"),
            InlineKeyboardButton("MB", callback_data=f"{CALLBACK_RESULT_VIEW_PREFIX}{draw_date}:MB"),
        ],
        [InlineKeyboardButton(t("BTN_BACK"), callback_data=CALLBACK_RESULT_MENU)],
    ]
    return InlineKeyboardMarkup(keyboard)


def _build_result_action_keyboard(draw_date: str, current_region: str, has_result: bool) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(t("BTN_REFRESH"), callback_data=f"{CALLBACK_RESULT_REFRESH_PREFIX}{draw_date}:{current_region}")],
        [
            InlineKeyboardButton("MN", callback_data=f"{CALLBACK_RESULT_VIEW_PREFIX}{draw_date}:MN"),
            InlineKeyboardButton("MT", callback_data=f"{CALLBACK_RESULT_VIEW_PREFIX}{draw_date}:MT"),
            InlineKeyboardButton("MB", callback_data=f"{CALLBACK_RESULT_VIEW_PREFIX}{draw_date}:MB"),
        ],
        [InlineKeyboardButton(t("BTN_CHANGE_DATE"), callback_data=CALLBACK_RESULT_CHANGE_DATE)],
        [InlineKeyboardButton(t("BTN_CLOSE") if has_result else t("BTN_BACK"), callback_data=CALLBACK_RESULT_CLOSE if has_result else CALLBACK_RESULT_MENU)],
    ]
    return InlineKeyboardMarkup(keyboard)


async def handle_result_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        return
    await query.answer()
    user_id = query.from_user.id if query.from_user else None
    log_step(f"🔎 Result menu callback | user_id={user_id if user_id is not None else 'N/A'} | data={query.data}")
    await query.edit_message_text(text=_build_result_menu_text(user_id), reply_markup=_build_result_date_keyboard())


async def handle_result_date_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        return
    await query.answer()
    user_id = query.from_user.id if query.from_user else None
    draw_date = query.data.replace(CALLBACK_RESULT_DATE_PREFIX, "", 1)
    log_step(
        f"🔎 Result date selected | user_id={user_id if user_id is not None else 'N/A'} "
        f"| draw_date={draw_date} | data={query.data}"
    )
    await query.edit_message_text(text=_build_result_region_text(draw_date, user_id), reply_markup=_build_result_region_keyboard(draw_date))


async def handle_result_view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        return
    await query.answer()
    user_id = query.from_user.id if query.from_user else None
    lang = _get_user_lang(user_id)
    payload = query.data.replace(CALLBACK_RESULT_VIEW_PREFIX, "", 1)
    try:
        draw_date, region_code = payload.split(":")
    except ValueError:
        log_step(f"❌ Result view payload invalid | user_id={user_id if user_id is not None else 'N/A'} | data={query.data}")
        await query.edit_message_text(t("PROMPT_INVALID_RESULT", lang))
        return
    log_step(
        f"📊 Result view requested | user_id={user_id if user_id is not None else 'N/A'} "
        f"| draw_date={draw_date} | region={region_code} | data={query.data}"
    )
    try:
        result_data = result_query_service.get_or_fetch(draw_date, region_code)
        meta = result_data.get("meta")
        items = result_data.get("items", [])
        message_text = format_result_message(meta, items, lang=lang)
        has_result = bool(meta and meta.get("status") == "available" and items)
        log_step(
            f"📊 Result view rendered | draw_date={draw_date} | region={region_code} "
            f"| status={(meta or {}).get('status', 'none') if meta else 'none'} | items={len(items)}"
        )
        await query.edit_message_text(
            text=_as_monospace_html(message_text),
            reply_markup=_build_result_action_keyboard(draw_date, region_code, has_result),
            parse_mode="HTML",
        )
    except Exception as exc:
        log_step(
            f"❌ Result view failed | user_id={user_id if user_id is not None else 'N/A'} "
            f"| draw_date={draw_date} | region={region_code} | error={exc}"
        )
        log_step(traceback.format_exc())
        await query.answer(text=t("PROMPT_INVALID_RESULT", lang), show_alert=True)


async def handle_result_refresh(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        return
    await query.answer()
    user_id = query.from_user.id if query.from_user else None
    lang = _get_user_lang(user_id)
    payload = query.data.replace(CALLBACK_RESULT_REFRESH_PREFIX, "", 1)
    try:
        draw_date, region_code = payload.split(":")
    except ValueError:
        log_step(f"❌ Result refresh payload invalid | user_id={user_id if user_id is not None else 'N/A'} | data={query.data}")
        await query.edit_message_text(t("PROMPT_INVALID_REFRESH", lang))
        return
    log_step(
        f"🔄 Result refresh requested | user_id={user_id if user_id is not None else 'N/A'} "
        f"| draw_date={draw_date} | region={region_code} | data={query.data}"
    )
    try:
        result_fetch_service.fetch_and_store(draw_date, region_code)
        result_data = result_query_service.get_or_fetch(draw_date, region_code)
        meta = result_data.get("meta")
        items = result_data.get("items", [])
        message_text = format_result_message(meta, items, lang=lang)
        has_result = bool(meta and meta.get("status") == "available" and items)
        log_step(
            f"🔄 Result refresh rendered | draw_date={draw_date} | region={region_code} "
            f"| status={(meta or {}).get('status', 'none') if meta else 'none'} | items={len(items)}"
        )
        await query.edit_message_text(
            text=_as_monospace_html(message_text),
            reply_markup=_build_result_action_keyboard(draw_date, region_code, has_result),
            parse_mode="HTML",
        )
    except Exception as exc:
        log_step(
            f"❌ Result refresh failed | user_id={user_id if user_id is not None else 'N/A'} "
            f"| draw_date={draw_date} | region={region_code} | error={exc}"
        )
        log_step(traceback.format_exc())
        await query.answer(text=t("PROMPT_INVALID_REFRESH", lang), show_alert=True)


async def handle_result_change_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        return
    await query.answer()
    user_id = query.from_user.id if query.from_user else None
    log_step(f"🔎 Result change date callback | user_id={user_id if user_id is not None else 'N/A'} | data={query.data}")
    await query.edit_message_text(text=_build_result_menu_text(user_id), reply_markup=_build_result_date_keyboard())


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
            await query.edit_message_text(t("PROMPT_CLOSED"))
        except Exception:
            pass


async def handle_application_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    callback_data = None
    if isinstance(update, Update) and update.callback_query:
        callback_data = update.callback_query.data
    error_trace = "".join(
        traceback.format_exception(None, context.error, context.error.__traceback__)
    ) if context.error else "No traceback available"
    log_step(
        f"❌ Unhandled application error | callback_data={callback_data or 'N/A'} "
        f"| error={context.error}"
    )
    log_step(error_trace)


async def result_entry_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_user:
        return
    user_id = update.effective_user.id
    await update.message.reply_text(text=_build_result_menu_text(user_id), reply_markup=_build_result_date_keyboard())


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
        if text == t("BTN_BACK", lang=_get_user_lang(user_id)):
            _set_user_state(user_id, UserState.IDLE)
            await show_main_menu(update, context)
            return
        # Menu button fallback while in BET_REGION → go to IDLE then handle
        if text in MENU_BUTTONS:
            _set_user_state(user_id, UserState.IDLE)
            await main_menu_handler(update, context)
            return
        await update.message.reply_text(t("PROMPT_SELECT_REGION_HINT", _get_user_lang(user_id)), reply_markup=_build_region_kb(lang=_get_user_lang(user_id)))
        return

    # ── State: ODI_DATE (Phase 1.1 ReplyKeyboard date picker) ──
    if state == UserState.ODI_DATE:
        lang = _get_user_lang(user_id)
        # "Today dd/mm" button
        if text == t("BTN_TODAY", lang=lang, date=_today_local_date().strftime("%d/%m")):
            _set_user_target_date(user_id, _today_iso())
            _set_user_state(user_id, UserState.BET_REGION)
            await _send_status_message(update, context, t("PROMPT_SELECT_REGION", lang), reply_markup=_build_region_kb(lang=lang))
            return
        # Date button: "dd/mm"
        if re.match(r"^\d{2}/\d{2}$", text):
            day, month = text.split("/")
            year = _today_local_date().year
            try:
                target_date = date(year, int(month), int(day)).isoformat()
            except ValueError:
                await _send_menu_message(update, context, t("PROMPT_INVALID_DATE", lang), _build_odi_kb(lang=lang))
                return
            _set_user_target_date(user_id, target_date)
            _set_user_state(user_id, UserState.BET_REGION)
            await _send_status_message(update, context, t("PROMPT_SELECT_REGION", lang), reply_markup=_build_region_kb(lang=lang))
            return
        # "Set Custom Date" button
        if text == t("BTN_SET_CUSTOM_DATE", lang=lang):
            _set_waiting_custom_date(user_id, True)
            await _send_status_message(update, context, t("PROMPT_ENTER_DATE", lang), reply_markup=ReplyKeyboardRemove())
            return
        # "⬅ Back" button
        if text == t("BTN_BACK", lang=lang):
            _set_user_state(user_id, UserState.IDLE)
            await show_main_menu(update, context)
            return
        # Menu button fallback while in ODI_DATE → go to IDLE then handle
        if text in MENU_BUTTONS:
            _set_user_state(user_id, UserState.IDLE)
            await main_menu_handler(update, context)
            return
        await _send_menu_message(update, context, t("PROMPT_SELECT_DATE_HINT", lang), _build_odi_kb(lang=lang))
        return

    # ── State: REPORT_TYPE (Phase 1.2 ReplyKeyboard type picker) ──
    if state == UserState.REPORT_TYPE:
        lang = _get_user_lang(user_id)
        type_map = {
            t("REPORT_LABEL_TRANSACTION", lang=lang): REPORT_TYPE_TRANSACTION,
            t("REPORT_LABEL_SETTLEMENT", lang=lang): REPORT_TYPE_SETTLEMENT,
            t("REPORT_LABEL_NUMBER_DETAIL", lang=lang): REPORT_TYPE_NUMBER_DETAIL,
            t("REPORT_LABEL_OVER_LIMIT", lang=lang): REPORT_TYPE_OVER_LIMIT,
        }
        if text in type_map:
            _set_user_state(user_id, UserState.REPORT_DATE)
            user_context[user_id]["report_type"] = type_map[text]
            await _send_status_message(update, context, t("PROMPT_SELECT_DATE", lang), reply_markup=_build_report_date_kb(lang=lang))
            return
        if text == t("BTN_BACK", lang=lang):
            _set_user_state(user_id, UserState.IDLE)
            await show_main_menu(update, context)
            return
        if text in MENU_BUTTONS:
            _set_user_state(user_id, UserState.IDLE)
            await main_menu_handler(update, context)
            return
        await update.message.reply_text(t("PROMPT_SELECT_REPORT_TYPE_HINT", lang), reply_markup=_build_report_type_kb(lang=lang))
        return

    # ── State: REPORT_DATE (Phase 1.2 ReplyKeyboard date picker) ──
    if state == UserState.REPORT_DATE:
        lang = _get_user_lang(user_id)
        report_type = user_context[user_id].get("report_type", REPORT_TYPE_TRANSACTION)
        # "Today dd/mm" button
        if text == t("BTN_TODAY", lang=lang, date=_today_local_date().strftime("%d/%m")):
            target_date = _today_iso()
            report_text = _generate_report_text(report_type, target_date, lang=lang)
            await _clear_menu_message(update, context)
            if report_text:
                await update.message.reply_text(
                    _as_monospace_html(report_text),
                    parse_mode="HTML",
                    reply_markup=_build_report_action_keyboard(report_type, target_date, lang=lang),
                )
            else:
                await update.message.reply_text(t("REPORT_COMING_SOON", lang=lang), reply_markup=ReplyKeyboardRemove())
                _set_user_state(user_id, UserState.IDLE)
                await show_main_menu(update, context)
            return
        # Date button: "dd/mm"
        if re.match(r"^\d{2}/\d{2}$", text):
            day, month = text.split("/")
            year = _today_local_date().year
            try:
                target_date = date(year, int(month), int(day)).isoformat()
            except ValueError:
                await _send_menu_message(update, context, t("PROMPT_INVALID_DATE", lang), _build_report_date_kb(lang=lang))
                return
            report_text = _generate_report_text(report_type, target_date, lang=lang)
            await _clear_menu_message(update, context)
            if report_text:
                await update.message.reply_text(
                    _as_monospace_html(report_text),
                    parse_mode="HTML",
                    reply_markup=_build_report_action_keyboard(report_type, target_date, lang=lang),
                )
            else:
                await update.message.reply_text(t("REPORT_COMING_SOON", lang=lang), reply_markup=ReplyKeyboardRemove())
                _set_user_state(user_id, UserState.IDLE)
                await show_main_menu(update, context)
            return
        # "⬅ Back" → return to report type selection
        if text == t("BTN_BACK", lang=lang):
            _set_user_state(user_id, UserState.REPORT_TYPE)
            await _send_status_message(update, context, t("PROMPT_SELECT_REPORT_TYPE", lang), reply_markup=_build_report_type_kb(lang=lang))
            return
        # Menu button fallback
        if text in MENU_BUTTONS:
            _set_user_state(user_id, UserState.IDLE)
            await main_menu_handler(update, context)
            return
        await _send_menu_message(update, context, t("PROMPT_SELECT_DATE_HINT", lang), _build_report_date_kb(lang=lang))
        return

    # ── State: ADMIN_WAITING (legacy admin text input) ──
    admin_waiting_action = _get_admin_waiting_action(user_id)
    if admin_waiting_action:
        if not admin_auth_service.is_admin(user_id):
            _set_admin_waiting_action(user_id, None)
            _set_user_state(user_id, UserState.IDLE)
            await update.message.reply_text(t("PROMPT_ACCESS_DENIED", _get_user_lang(user_id)))
            return

        if text in MENU_BUTTONS:
            _set_admin_waiting_action(user_id, None)
            _set_user_state(user_id, UserState.IDLE)
            await main_menu_handler(update, context)
            return

        try:
            if admin_waiting_action == "ADD_ADMIN":
                if not text.isdigit():
                    await update.message.reply_text(t("ADMIN_INVALID_USER_ID", _get_user_lang(user_id)))
                    return
                admin_auth_service.add_admin(text)
                _set_admin_waiting_action(user_id, None)
                await update.message.reply_text(t("ADMIN_ADDED_USER", _get_user_lang(user_id), user_id=text))
                await update.message.reply_text(text=_build_set_admin_text(), reply_markup=_build_set_admin_keyboard())
                return

            if admin_waiting_action == "REMOVE_ADMIN":
                if not text.isdigit():
                    await update.message.reply_text(t("ADMIN_INVALID_USER_ID", _get_user_lang(user_id)))
                    return
                _, message = admin_auth_service.remove_admin(text)
                _set_admin_waiting_action(user_id, None)
                await update.message.reply_text(message)
                await update.message.reply_text(text=_build_set_admin_text(), reply_markup=_build_set_admin_keyboard())
                return

            if admin_waiting_action == "SET_AGENT_COMM":
                normalized = admin_settings_service.set_agent_commission_rate(text)
                _set_admin_waiting_action(user_id, None)
                await update.message.reply_text(t("ADMIN_AGENT_COMM_UPDATED", _get_user_lang(user_id), value=normalized))
                await update.message.reply_text(text=t("ADMIN_AGENT_COMM_SETTING", _get_user_lang(user_id)), reply_markup=_build_agent_comm_keyboard())
                return

            if admin_waiting_action == "SET_BONUS_PAYOUT_BULK":
                admin_settings_service.update_bonus_payout_bulk(text)
                _set_admin_waiting_action(user_id, None)
                await update.message.reply_text(t("ADMIN_BONUS_PAYOUT_UPDATED", _get_user_lang(user_id)))
                await update.message.reply_text(text=admin_settings_service.format_bonus_payout_text(lang=_get_user_lang(user_id)), reply_markup=_build_bonus_payout_keyboard())
                return

            if admin_waiting_action == "SET_OVER_LIMIT_BULK":
                admin_settings_service.update_limit_bulk(text)
                _set_admin_waiting_action(user_id, None)
                await update.message.reply_text(t("ADMIN_OVER_LIMIT_UPDATED", _get_user_lang(user_id)))
                await update.message.reply_text(text=admin_settings_service.format_limit_text(lang=_get_user_lang(user_id)), reply_markup=_build_over_limit_keyboard())
                return

            if admin_waiting_action == "SET_CUTOFF_TIME_BULK":
                admin_settings_service.update_cutoff_time_bulk(text)
                _set_admin_waiting_action(user_id, None)
                await update.message.reply_text(t("ADMIN_CUTOFF_TIME_UPDATED", _get_user_lang(user_id)))
                await update.message.reply_text(text=admin_settings_service.format_cutoff_time_text(lang=_get_user_lang(user_id)), reply_markup=_build_time_limit_keyboard())
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
            await update.message.reply_text(t("ADMIN_INVALID_DATE_FORMAT", _get_user_lang(user_id)))
            return
        _set_user_target_date(user_id, parsed_date)
        _set_user_state(user_id, UserState.BET_INPUT)
        _set_user_region(user_id, None)  # force re-select via /mn /mt /mb
        await _clear_menu_message(update, context)
        await update.message.reply_text(t("MENU_OTHER_DAY_INPUT", _get_user_lang(user_id)), reply_markup=ReplyKeyboardRemove())
        await _send_menu_message(update, context, t("MENU_BET", _get_user_lang(user_id)), get_bet_menu_keyboard())
        return

    # ── State: RESULT_DATE (Phase 1.3 ReplyKeyboard date picker) ──
    if state == UserState.RESULT_DATE:
        lang = _get_user_lang(user_id)
        # "Today dd/mm" button
        if text == t("BTN_TODAY", lang=lang, date=_today_local_date().strftime("%d/%m")):
            draw_date = _today_iso()
            _set_user_result_draw_date(user_id, draw_date)
            _set_user_state(user_id, UserState.RESULT_REGION)
            await _send_status_message(update, context, t("PROMPT_SELECT_REGION", lang), reply_markup=_build_result_region_kb(lang=lang))
            return
        # Date button: "dd/mm"
        if re.match(r"^\d{2}/\d{2}$", text):
            day, month = text.split("/")
            year = _today_local_date().year
            try:
                draw_date = date(year, int(month), int(day)).isoformat()
            except ValueError:
                await _send_status_message(update, context, t("PROMPT_INVALID_DATE", lang), reply_markup=_build_result_date_kb(lang=lang))
                return
            _set_user_result_draw_date(user_id, draw_date)
            _set_user_state(user_id, UserState.RESULT_REGION)
            await _send_status_message(update, context, t("PROMPT_SELECT_REGION", lang), reply_markup=_build_result_region_kb(lang=lang))
            return
        # "⬅ Back" button
        if text == t("BTN_BACK", lang=lang):
            _set_user_state(user_id, UserState.IDLE)
            await show_main_menu(update, context)
            return
        # Menu button fallback while in RESULT_DATE → go to IDLE then handle
        if text in MENU_BUTTONS:
            _set_user_state(user_id, UserState.IDLE)
            await main_menu_handler(update, context)
            return
        await _send_menu_message(update, context, t("PROMPT_SELECT_DATE_HINT", lang), _build_result_date_kb(lang=lang))
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
            message_text = format_result_message(meta, items, lang=_get_user_lang(user_id))
            await _clear_transient_messages(update, context)
            await update.message.reply_text(_as_monospace_html(message_text), parse_mode="HTML", reply_markup=ReplyKeyboardRemove())
            # Show result action keyboard (ReplyKeyboard style)
            await _send_status_message(update, context, t("PROMPT_RESULT_ACTIONS", _get_user_lang(user_id)), reply_markup=_build_result_region_kb(lang=_get_user_lang(user_id)))
            return
        if text == t("BTN_BACK", lang=_get_user_lang(user_id)):
            _set_user_state(user_id, UserState.RESULT_DATE)
            await _send_status_message(update, context, _build_result_menu_text(user_id), reply_markup=_build_result_date_kb(lang=_get_user_lang(user_id)))
            return
        # Menu button fallback while in RESULT_REGION → go to IDLE then handle
        if text in MENU_BUTTONS:
            _set_user_state(user_id, UserState.IDLE)
            await main_menu_handler(update, context)
            return
        await update.message.reply_text(t("PROMPT_SELECT_REGION_HINT", _get_user_lang(user_id)), reply_markup=_build_result_region_kb(lang=_get_user_lang(user_id)))
        return

    # ── State: ADMIN_MENU (Phase 1.4 ReplyKeyboard admin menu) ──
    if state == UserState.ADMIN_MENU:
        lang = _get_user_lang(user_id)

        if text == f"1. {t('ADMIN_AGENT_COMM_SETTING', lang=lang)}":
            await _send_menu_message(update, context, t('ADMIN_AGENT_COMM_SETTING', lang=lang), _build_agent_comm_keyboard(lang=lang))
            return

        if text == f"2. {t('ADMIN_BONUS_PAYOUT_SETTING', lang=lang)}":
            await _send_menu_message(update, context, t('ADMIN_BONUS_PAYOUT_SETTING', lang=lang), _build_bonus_payout_keyboard(lang=lang))
            return

        if text == f"3. {t('ADMIN_OVER_LIMIT_SETTING', lang=lang)}":
            await _send_menu_message(update, context, t('ADMIN_OVER_LIMIT_SETTING', lang=lang), _build_over_limit_keyboard(lang=lang))
            return

        if text == f"4. {t('ADMIN_NOTIFICATIONS', lang=lang)}":
            await _send_menu_message(update, context, t('ADMIN_NOTIFICATIONS', lang=lang), _build_notifications_keyboard(lang=lang))
            return

        if text == f"5. {t('ADMIN_BET_TIME_LIMIT', lang=lang)}":
            await _send_menu_message(update, context, t('ADMIN_BET_TIME_LIMIT', lang=lang), _build_time_limit_keyboard(lang=lang))
            return

        if text == f"6. {t('ADMIN_SYSTEM_TIME_ZONE', lang=lang)}":
            await _send_menu_message(update, context, t('ADMIN_SYSTEM_TIME_ZONE', lang=lang), _build_system_timezone_keyboard(lang=lang))
            return

        if text == f"7. {t('ADMIN_SET_ADMIN', lang=lang)}":
            await _send_menu_message(update, context, _build_set_admin_text(lang=lang), _build_set_admin_keyboard(lang=lang))
            return

        if text == t("BTN_BACK", lang=lang):
            _set_user_state(user_id, UserState.IDLE)
            await show_main_menu(update, context)
            return

        if text in MENU_BUTTONS:
            _set_user_state(user_id, UserState.IDLE)
            await main_menu_handler(update, context)
            return

        await _send_menu_message(update, context, t("PROMPT_SELECT_ADMIN_OPTION", _get_user_lang(user_id)), _build_admin_menu_kb())
        return

    # ── Main menu buttons (IDLE or fallback) ──
    if text in MENU_BUTTONS:
        await main_menu_handler(update, context)
        return

    # ── Delete command ──
    if text.lower().startswith("delete"):
        parts = text.split()
        if len(parts) < 2:
            await update.message.reply_text(t("ADMIN_USAGE_DELETE_TEXT", _get_user_lang(user_id)))
            return
        ticket_no = parts[1].upper()
        target_date = _get_user_target_date(user_id)
        _, response_text = delete_ticket(ticket_no, target_date, lang=_get_user_lang(user_id))
        await _clear_menu_message(update, context)
        await update.message.reply_text(_as_monospace_html(_build_delete_success_message(response_text)), parse_mode="HTML", reply_markup=ReplyKeyboardRemove())
        return

    # ── Bet input (state BET_INPUT or legacy region set) ──
    current_region = _get_user_region(user_id)
    if current_region:
        await bet_handler(update, context)
        return

    await _clear_menu_message(update, context)
    await update.message.reply_text(t("PROMPT_SELECT_REGION_FIRST", _get_user_lang(user_id)), reply_markup=ReplyKeyboardRemove())


async def bet_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.effective_user:
        return
    user_id = update.effective_user.id
    text = update.message.text
    region_group = _get_user_region(user_id)
    target_date = _get_user_target_date(user_id)
    if not region_group:
        await _clear_transient_messages(update, context)
        await update.message.reply_text(t("PROMPT_SELECT_REGION_FIRST", _get_user_lang(user_id)), reply_markup=ReplyKeyboardRemove())
        return
    try:
        _, response_text = process_bet_message(user_id=str(user_id), region_group=region_group, text=text, target_date=target_date, lang=_get_user_lang(user_id))
        await _clear_transient_messages(update, context)
        await update.message.reply_text(_as_monospace_html(response_text), parse_mode="HTML", reply_markup=ReplyKeyboardRemove())
    except Exception as e:
        await update.message.reply_text(f"System Error: {str(e)}")


# =========================================================
# App builder
# =========================================================
def build_application() -> Application:
    global admin_auth_service, admin_settings_service, agent_customer_repository, user_pref_repo

    log_step("🤖 Building Telegram application ...")

    # 从环境变量读取最新配置，避免模块导入时提前缓存旧值
    bot_token = os.getenv("BOT_TOKEN")
    default_admin_user_ids = os.getenv("DEFAULT_ADMIN_USER_IDS", "")

    if not bot_token:
        raise RuntimeError("BOT_TOKEN not found in environment variables")

    # 依赖环境变量的服务必须在配置加载后初始化
    admin_auth_service = AdminAuthService(default_admin_ids_str=default_admin_user_ids)
    admin_settings_service = AdminSettingsService()
    agent_customer_repository = AgentCustomerRepository()
    user_pref_repo = UserPreferenceRepository()

    application = ApplicationBuilder().token(bot_token).post_init(post_init).build()
    application.bot_data["chat_scope_config"] = _get_chat_scope_config()

    log_step("🧩 Registering handlers ...")
    application.add_handler(TypeHandler(Update, enforce_chat_scope), group=-1)
    application.add_handler(ChatMemberHandler(handle_bot_joined_group, ChatMemberHandler.MY_CHAT_MEMBER))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("result", result_entry_command))
    application.add_handler(CommandHandler("myid", myid_command))
    application.add_handler(CommandHandler("mn", mn_command))
    application.add_handler(CommandHandler("mt", mt_command))
    application.add_handler(CommandHandler("mb", mb_command))
    application.add_handler(CommandHandler("delete", delete_command))
    application.add_handler(CommandHandler("settlement", settlement_today_command))
    application.add_handler(CommandHandler("lang", lang_command))
    application.add_handler(CallbackQueryHandler(handle_lang_select, pattern=f"^{CALLBACK_LANG_SET_PREFIX}"))

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
    application.add_error_handler(handle_application_error)
    return application


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='M33 Lotto Bot')
    parser.add_argument('--config-dir', type=str, help='配置目录路径')
    args = parser.parse_args()
    
    try:
        # 加载配置
        config = load_config(args.config_dir)
        
        # 设置环境变量（覆盖任何现有值）
        os.environ['DB_PATH'] = config['DB_PATH']
        os.environ['BOT_TOKEN'] = config['BOT_TOKEN']
        os.environ['CLIENT_NAME'] = config.get('CLIENT_NAME', 'default_client')
        os.environ['DEFAULT_LANGUAGE'] = config.get('DEFAULT_LANGUAGE', 'vi')
        os.environ['ALLOWED_GROUP_ID'] = config.get('ALLOWED_GROUP_ID_RAW', '')
        
        # 设置其他环境变量
        if config.get('ADMIN_CHAT_ID'):
            os.environ['ADMIN_CHAT_ID'] = config['ADMIN_CHAT_ID']
        if config.get('DEFAULT_ADMIN_USER_IDS'):
            os.environ['DEFAULT_ADMIN_USER_IDS'] = config['DEFAULT_ADMIN_USER_IDS']
        
        # 设置时区
        if 'TIMEZONE' in config:
            os.environ['TZ'] = config['TIMEZONE']
        
        # 验证Bot Token
        bot_token = config['BOT_TOKEN']
        if not bot_token:
            print("错误: BOT_TOKEN未配置")
            return
        
        print(f"✅ 配置加载完成")
        print(f"   客户: {config.get('CLIENT_NAME', 'N/A')}")
        print(f"   数据库: {config['DB_PATH']}")
        print(f"   Allowed Group: {config.get('ALLOWED_GROUP_ID_RAW') or 'NOT CONFIGURED'}")
        print(f"   Token: {bot_token[:15]}...")
        
        # 设置日志（如果需要）
        if 'LOG_PATH' in config:
            import logging
            logging.basicConfig(
                filename=config['LOG_PATH'],
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        
        # 这里继续原有的启动代码...
        # 确保使用 config['BOT_TOKEN'] 而不是硬编码的TOKEN
        
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        return
    
    try:
        validate_environment()
        initialize_database()
        application = build_application()
        log_step("▶ Starting polling ...")
        application.run_polling()
    except Exception as e:
        log_step(f"❌ Startup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
