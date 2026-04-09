# English (base language) â€” all keys must be defined here.
# Other language files may omit keys; missing keys fall back to this file.

STRINGS: dict[str, str] = {
    # â”€â”€ Main menu buttons â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    "BTN_BET": "Bet",
    "BTN_REPORT": "Report",
    "BTN_RESULT": "Result",
    "BTN_OTHER_DAY_INPUT": "Other Day Input",
    "BTN_ADMIN": "Admin",
    "BTN_INFO": "Info",

    # â”€â”€ Common buttons â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    "BTN_BACK": "⬅ Back",
    "BTN_CLOSE": "❌ Close",
    "BTN_REFRESH": "🔄 Refresh",
    "BTN_CHANGE_DATE": "📅 Change Date",
    "BTN_EXPORT_HTML": "📄 Export HTML",
    "BTN_SET_CUSTOM_DATE": "Set Custom Date",
    # {date} is replaced at runtime with dd/mm string
    "BTN_TODAY": "Today {date}",

    # â”€â”€ Common prompts â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    "PROMPT_SELECT_REGION": "Select region:",
    "PROMPT_SELECT_DATE": "Select date:",
    "PROMPT_SELECT_REPORT_TYPE": "Select report type:",
    "PROMPT_SELECT_ADMIN_OPTION": "Please select an admin option.",
    "PROMPT_RESULT_ACTIONS": "Result actions:",
    "PROMPT_CLOSED": "Closed.",
    "PROMPT_INVALID_REPORT": "Invalid report request.",
    "PROMPT_INVALID_EXPORT": "Invalid export request.",
    "PROMPT_EXPORT_UNAVAILABLE": "Export not available.",
    "PROMPT_INVALID_RESULT": "Invalid result request.",
    "PROMPT_INVALID_REFRESH": "Invalid refresh request.",
    "PROMPT_INVALID_REGION": "Invalid region. Please select MN, MT, or MB.",
    "PROMPT_SELECT_REGION_HINT": "Please select a region (MN / MT / MB).",
    "PROMPT_SELECT_DATE_HINT": "Please select a date.",
    "PROMPT_SELECT_REPORT_TYPE_HINT": "Please select a report type.",
    "PROMPT_INVALID_DATE": "❌ Invalid date.",
    "PROMPT_ENTER_DATE": "Please enter date (YYYY-MM-DD):",
    "PROMPT_CUSTOM_DATE": "Custom Date\n\nYYYY-MM-DD",
    "PROMPT_ACCESS_DENIED": "You do not have permission to access this feature.",
    "PROMPT_INVALID_DATE_FORMAT": "❌ Invalid date format. Please enter YYYY-MM-DD",
    "PROMPT_SELECT_REGION_FIRST": "Please select region first.\nUse /mn /mt /mb",
    "BET_MODE_ACTIVE": "You are now in {region} bet mode.",
    "LABEL_DATE": "Date: {date}",
    "LABEL_TODAY_SUFFIX": "(Today)",

    # â”€â”€ Info panel â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    "INFO_TITLE": "INFO",
    "INFO_REGION_CODE": "REGION CODE",
    "INFO_FURTHER": "FOR FURTHER INFORMATION",
    "INFO_TELEGRAM": "Telegram: @M33_VN",
    # {version} is replaced at runtime
    "INFO_VERSION": "Version : {version}",

    # â”€â”€ Language selection â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # Shown in all 3 languages at once so any user can understand it
    "LANG_SELECT_PROMPT": "🌐 Select language / 选择语言 / Chọn ngôn ngữ",
    "LANG_SET_EN": "✅ Language set to English",
    "LANG_SET_ZH": "✅ Language set to Chinese",
    "LANG_SET_VI": "✅ Language set to Vietnamese",

    # â”€â”€ Admin settings service format_*() output â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    "ADMIN_FORMAT_BET_TIME_LIMIT": "Bet Time Limit",
    # {tz} = timezone name string
    "ADMIN_FORMAT_TIMEZONE_LINE": "Timezone: {tz}",
    "ADMIN_FORMAT_SYSTEM_TIME_ZONE": "System Time Zone",
    # {value} = current value string
    "ADMIN_FORMAT_CURRENT_LINE": "Current: {value}",
    "ADMIN_FORMAT_BONUS_PAYOUT_SETTINGS": "Bonus Payout Settings",
    "ADMIN_FORMAT_OVER_LIMIT_SETTINGS": "Over Limit Settings",
    "ADMIN_FORMAT_NOTIFICATIONS": "Notifications",
    # {status} = ENABLED / DISABLED (internal constant, not translated)
    "ADMIN_FORMAT_CUSTOMER_NOTIF": "Customer Notification: {status}",
    # {action} = ACCEPT / REJECT (internal constant, not translated)
    "ADMIN_FORMAT_OVER_LIMIT_ACTION": "Over Limit Action: {action}",

    # â”€â”€ Bet delete responses â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # {ticket_no} = ticket number string
    "BET_DELETE_NOT_FOUND": "❌ Ticket not found: {ticket_no}",
    # {ticket_no}, {date} = ticket number, target date
    "BET_DELETE_NOT_FOUND_WITH_DATE": "❌ Ticket not found: {ticket_no}\nDate: {date}",
    # {ticket_no} = ticket number string
    "BET_DELETE_ALREADY_DELETED": "❌ Ticket already deleted: {ticket_no}",
    # {ticket_no}, {date} = ticket number, target date
    "BET_DELETE_ALREADY_DELETED_WITH_DATE": "❌ Ticket already deleted: {ticket_no}\nDate: {date}",
    # {region} = region group, {ticket_no} = ticket number
    "BET_DELETE_SUCCESS": "🗑 Deleted · {region} · {ticket_no}",
    # {region}, {ticket_no}, {date} = region group, ticket number, target date
    "BET_DELETE_SUCCESS_WITH_DATE": "🗑 Deleted · {region} · {ticket_no}\nDate: {date}",

    # â”€â”€ Admin panel menu titles â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    "ADMIN_AGENT_COMM_SETTING": "Agent Comm Setting",
    "ADMIN_OVER_LIMIT_SETTING": "Over Limit Setting",
    "ADMIN_NOTIFICATIONS": "Notifications",
    "ADMIN_BET_TIME_LIMIT": "Bet Time Limit",
    "ADMIN_SYSTEM_TIME_ZONE": "System Time Zone",
    "ADMIN_USAGE_DELETE_SLASH": "❌ Usage: /delete N1",
    "ADMIN_USAGE_DELETE_TEXT": "❌ Usage: delete N1",

    # â”€â”€ Bet / Other Day menu labels â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    "MENU_OTHER_DAY_INPUT": "Other Day Input",
    "MENU_BET": "Bet",

    # â”€â”€ Admin panel dynamic templates â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # {rate} = current commission rate (numeric string)
    "ADMIN_AGENT_COMM_CURRENT": "Agent Commission Rate\n\nCurrent: {rate}%",
    # {action} = ACCEPT or REJECT
    "ADMIN_OVER_LIMIT_CURRENT": "Over Limit Action\n\nCurrent: {action}",
    # {user_id} = numeric user id string
    "ADMIN_ADDED_USER": "✅ Admin added\nUser ID: {user_id}",
    # {value} = normalized commission rate after update
    "ADMIN_AGENT_COMM_UPDATED": "✅ Agent Commission updated\nCurrent: {value}%",

    # â”€â”€ Admin panel input validation â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    "ADMIN_INVALID_USER_ID": "❌ Invalid user id. Please enter digits only.",
    "ADMIN_INVALID_DATE_FORMAT": "❌ Invalid date format.\nPlease use YYYY-MM-DD",
    "ADMIN_ENTER_COMMISSION_RATE": "Please enter new commission rate (%):",
    "ADMIN_BONUS_PAYOUT_SETTING": "Bonus Payout Setting",
    "ADMIN_BONUS_PAYOUT_UPDATED": "✅ Bonus Payout updated",
    "ADMIN_OVER_LIMIT_UPDATED": "✅ Over Limit updated",
    "ADMIN_CUTOFF_TIME_UPDATED": "✅ Cutoff Time updated",
    "ADMIN_SET_ADMIN": "Set Admin",
    "ADMIN_VIEW_ADMIN_LIST": "View Admin List",
    "ADMIN_ADD_ADMIN": "Add Admin",
    "ADMIN_REMOVE_ADMIN": "Remove Admin",
    "ADMIN_VIEW_CURRENT_AGENT_COMM": "View Current Agent Comm",
    "ADMIN_EDIT_AGENT_COMM": "Edit Agent Comm",
    "ADMIN_VIEW_CURRENT_BONUS_PAYOUT": "View Current Bonus Payout",
    "ADMIN_EDIT_BONUS_PAYOUT": "Edit Bonus Payout",
    "ADMIN_VIEW_CURRENT_OVER_LIMIT": "View Current Over Limit",
    "ADMIN_EDIT_OVER_LIMIT": "Edit Over Limit",
    "ADMIN_SET_OVER_LIMIT_ACTION": "Set Over Limit Action",
    "ADMIN_CONTINUE_ACCEPTING": "Continue Accepting",
    "ADMIN_REJECT_BET": "Reject Bet",
    "ADMIN_VIEW_CURRENT_NOTIFICATION_SETTINGS": "View Current Notification Settings",
    "ADMIN_ON": "ON",
    "ADMIN_OFF": "OFF",
    "ADMIN_VIEW_CURRENT_CUTOFF_TIME": "View Current Cutoff Time",
    "ADMIN_EDIT_CUTOFF_TIME": "Edit Cutoff Time",
    "ADMIN_VIEW_CURRENT_TIME_ZONE": "View Current Time Zone",
    "ADMIN_TIMEZONE_KL": "Kuala Lumpur",
    "ADMIN_TIMEZONE_HCM": "Ho Chi Minh",
    "ADMIN_PROMPT_ADD_ADMIN": "Please enter Telegram user id to add as ADMIN:",
    "ADMIN_PROMPT_REMOVE_ADMIN": "Please enter Telegram user id to remove from ADMIN:",

    # â”€â”€ Admin panel status confirmations â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    "ADMIN_OVER_LIMIT_SET_ACCEPT": "✅ Over Limit Action set to ACCEPT",
    "ADMIN_OVER_LIMIT_SET_REJECT": "✅ Over Limit Action set to REJECT",
    "ADMIN_NOTIF_SET_ON": "✅ Customer Notification set to ON",
    "ADMIN_NOTIF_SET_OFF": "✅ Customer Notification set to OFF",
    "ADMIN_TIMEZONE_SET_KL": "✅ System Time Zone set to Asia/Kuala_Lumpur",
    "ADMIN_TIMEZONE_SET_HCM": "✅ System Time Zone set to Asia/Ho_Chi_Minh",

    # â”€â”€ Report menu handler â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    "REPORT_OVER_LIMIT_TITLE": "⚠️ Over Limit Report",
    "REPORT_SELECT_TYPE_TITLE": "📊 Select Report Type",
    # {error} is replaced at runtime with the exception message
    "REPORT_GENERATE_FAILED": "❌ Report generation failed: {error}",

    # â”€â”€ Report labels (menu layer) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    "REPORT_MENU_TITLE": "Report",
    "REPORT_LABEL_TRANSACTION": "Transaction",
    "REPORT_LABEL_SETTLEMENT": "Settlement",
    "REPORT_LABEL_NUMBER_DETAIL": "Number Detail",
    "REPORT_LABEL_OVER_LIMIT": "Over Limit",
    "REPORT_COMING_SOON": "Coming Soon",
    "REPORT_NO_DATA": "No data available.",

    # â”€â”€ Shared table column headers (bet + report formatters) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    "COL_REGION": "Region",
    "COL_NUMBER": "Number",
    "COL_MODE": "Mode",
    "COL_TOTAL": "Total",
    "COL_BET": "Bet",
    "COL_WIN": "Win",

    # â”€â”€ Bet formatter â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    "BET_ACCEPTED": "✅ Bet Accepted",
    # {value} is replaced at runtime with formatted total amount
    "BET_TOTAL_LINE": "💰 Total: {value}",
    "BET_INVALID_INPUT": "Invalid Input",
    "BET_SCHEDULE_CLOSED": "Region not open for selected date",

    # â”€â”€ Bet service â€” test mode â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    "BET_TEST_MODE_NOTICE": "⚠ TEST MODE · HISTORY BET ALLOWED FOR ADMIN",

    # â”€â”€ Bet service â€” over-limit notification â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    "BET_OVER_LIMIT_ACCEPT": "⚠️ Over limit reached\nContinue Accepting",
    "BET_OVER_LIMIT_REJECT": "⚠️ Over limit reached\nReject Bet",
    # {value} is replaced at runtime with the raw input text
    "BET_OVER_LIMIT_INPUT": "Input: {value}",

    # â”€â”€ Bet service â€” cutoff closed â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    "BET_CUTOFF_CLOSED": "⚠️ Betting closed",
    # {region} and {time} are replaced at runtime
    "BET_CUTOFF_REGION_TIME": "{region} closed at {time}",

    # â”€â”€ Result formatter â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    "RESULT_TITLE": "📊 RESULT",
    "RESULT_DATE_LABEL": "📅 Date:",
    "RESULT_NOT_AVAILABLE": "Result not available yet.",
    "RESULT_FETCHED_LABEL": "🕒 Fetched:",

    # â”€â”€ Report formatters (body text) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    "REPORT_TRANSACTION_TITLE": "📊 Transaction Report",
    "REPORT_SETTLEMENT_TITLE": "📘 Settlement Report",
    "REPORT_NUMBER_DETAIL_TITLE": "🔢 Number Detail Report",
    # {date} is replaced at runtime
    "REPORT_DATE_LABEL": "Date: {date}",
    # used inside formatter body when a region has no ticket data
    "REPORT_REGION_NO_DATA": "No data",
    # used inside formatter body when a ticket has no line items
    "REPORT_TICKET_NO_DETAIL": "No detail",
    # {value} is replaced at runtime with formatted amount
    "REPORT_TICKET_TOTAL": "Ticket Total: {value}",
    "REPORT_TICKET_WIN": "Ticket Win: {value}",
    "REPORT_BET_TOTAL": "Bet Total",
    "REPORT_PAYOUT": "Payout",
    "REPORT_AGENT_COMM": "Agent Comm",
    # {region} is replaced at runtime with region code (MN / MT / MB)
    "REPORT_REGION_SETTLEMENT": "{region} Settlement",
    "REPORT_TOTAL_SETTLEMENT": "Total Settlement",
    "REPORT_WINNING_DETAILS": "Winning Details",
    "REPORT_NO_WINNING": "No winning records",
    # {ts} is replaced at runtime with timestamp string
    "REPORT_GENERATED_AT": "🕒 Generated at: {ts} (UTC+8)",
    "REPORT_TOO_MANY_RECORDS": "⚠️ Too many records: {tickets} tickets, {lines} lines",
    "REPORT_USE_EXPORT": "📄 Please use Export HTML for full report",
    "REPORT_REGION_SUMMARY": "📍 {region}: {tickets} tickets, {lines} lines, total: {total}",
    "REPORT_NUMBER_ENTRY_SUMMARY": "{region}: {count} number entries",
    "REPORT_TRUNCATED": "📝 Report truncated due to length limit",
    "BOT_SCOPE_PRIVATE_ONLY": "This bot is only available in the authorized group.",
    "BOT_SCOPE_UNAUTHORIZED_GROUP": "This bot is not authorized for use in this group.",
    # â”€â”€ Telegram command menu descriptions â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    "CMD_START":      "Main menu",
    "CMD_MN":         "Bet MN (Today)",
    "CMD_MT":         "Bet MT (Today)",
    "CMD_MB":         "Bet MB (Today)",
    "CMD_SETTLEMENT": "Today settlement report",
}

