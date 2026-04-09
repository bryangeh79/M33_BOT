# Chinese (Simplified) â€” keys not defined here fall back to en.py.

STRINGS: dict[str, str] = {
    # â”€â”€ Main menu buttons â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    "BTN_BET": "æŠ•æ³¨",
    "BTN_REPORT": "æŠ¥è¡¨",
    "BTN_RESULT": "å¼€å¥–ç»“æžœ",
    "BTN_OTHER_DAY_INPUT": "å…¶ä»–æ—¥æœŸæŠ•æ³¨",
    "BTN_ADMIN": "ç®¡ç†",
    "BTN_INFO": "ä¿¡æ¯",

    # â”€â”€ Common buttons â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    "BTN_BACK": "â¬… è¿”å›ž",
    "BTN_CLOSE": "âŒ å…³é—­",
    "BTN_REFRESH": "ðŸ”„ åˆ·æ–°",
    "BTN_CHANGE_DATE": "ðŸ“… æ›´æ”¹æ—¥æœŸ",
    "BTN_EXPORT_HTML": "ðŸ“„ å¯¼å‡º HTML",
    "BTN_SET_CUSTOM_DATE": "è®¾ç½®è‡ªå®šä¹‰æ—¥æœŸ",
    "BTN_TODAY": "ä»Šå¤© {date}",

    # â”€â”€ Common prompts â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    "PROMPT_SELECT_REGION": "é€‰æ‹©åœ°åŒºï¼š",
    "PROMPT_SELECT_DATE": "é€‰æ‹©æ—¥æœŸï¼š",
    "PROMPT_SELECT_REPORT_TYPE": "é€‰æ‹©æŠ¥è¡¨ç±»åž‹ï¼š",
    "PROMPT_SELECT_ADMIN_OPTION": "è¯·é€‰æ‹©ç®¡ç†é€‰é¡¹ã€‚",
    "PROMPT_RESULT_ACTIONS": "ç»“æžœæ“ä½œï¼š",
    "PROMPT_CLOSED": "å·²å…³é—­ã€‚",
    "PROMPT_INVALID_REPORT": "æ— æ•ˆçš„æŠ¥è¡¨è¯·æ±‚ã€‚",
    "PROMPT_INVALID_EXPORT": "æ— æ•ˆçš„å¯¼å‡ºè¯·æ±‚ã€‚",
    "PROMPT_EXPORT_UNAVAILABLE": "å¯¼å‡ºä¸å¯ç”¨ã€‚",
    "PROMPT_INVALID_RESULT": "æ— æ•ˆçš„ç»“æžœè¯·æ±‚ã€‚",
    "PROMPT_INVALID_REFRESH": "æ— æ•ˆçš„åˆ·æ–°è¯·æ±‚ã€‚",
    "PROMPT_INVALID_REGION": "æ— æ•ˆåœ°åŒºã€‚è¯·é€‰æ‹© MNã€MT æˆ– MBã€‚",
    "PROMPT_SELECT_REGION_HINT": "è¯·é€‰æ‹©åœ°åŒºï¼ˆMN / MT / MBï¼‰ã€‚",
    "PROMPT_SELECT_DATE_HINT": "è¯·é€‰æ‹©æ—¥æœŸã€‚",
    "PROMPT_SELECT_REPORT_TYPE_HINT": "è¯·é€‰æ‹©æŠ¥è¡¨ç±»åž‹ã€‚",
    "PROMPT_INVALID_DATE": "âŒ æ— æ•ˆæ—¥æœŸã€‚",
    "PROMPT_ENTER_DATE": "è¯·è¾“å…¥æ—¥æœŸï¼ˆYYYY-MM-DDï¼‰ï¼š",
    "PROMPT_CUSTOM_DATE": "è‡ªå®šä¹‰æ—¥æœŸ\n\nYYYY-MM-DD",
    "PROMPT_ACCESS_DENIED": "æ‚¨æ²¡æœ‰æƒé™è®¿é—®æ­¤åŠŸèƒ½ã€‚",
    "PROMPT_INVALID_DATE_FORMAT": "âŒ æ—¥æœŸæ ¼å¼æ— æ•ˆã€‚è¯·è¾“å…¥ YYYY-MM-DD",
    "PROMPT_SELECT_REGION_FIRST": "è¯·å…ˆé€‰æ‹©åœ°åŒºã€‚\nä½¿ç”¨ /mn /mt /mb",
    "BET_MODE_ACTIVE": "æ‚¨çŽ°åœ¨å¤„äºŽ {region} æŠ•æ³¨æ¨¡å¼ã€‚",
    "LABEL_DATE": "æ—¥æœŸï¼š{date}",
    "LABEL_TODAY_SUFFIX": "ï¼ˆä»Šå¤©ï¼‰",

    # â”€â”€ Info panel â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    "INFO_TITLE": "ä¿¡æ¯",
    "INFO_REGION_CODE": "åœ°åŒºä»£ç ",
    "INFO_FURTHER": "å¦‚éœ€è¿›ä¸€æ­¥ä¿¡æ¯",
    "INFO_TELEGRAM": "Telegram: @M33_VN",
    "INFO_VERSION": "ç‰ˆæœ¬ï¼š{version}",

    # â”€â”€ Language selection â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    "LANG_SELECT_PROMPT": "ðŸŒ Select language / é€‰æ‹©è¯­è¨€ / Chá»n ngÃ´n ngá»¯",
    "LANG_SET_EN": "âœ… Language set to English",
    "LANG_SET_ZH": "âœ… è¯­è¨€å·²è®¾ä¸ºä¸­æ–‡",
    "LANG_SET_VI": "âœ… ÄÃ£ chá»n Tiáº¿ng Viá»‡t",

    # â”€â”€ Admin settings service format_*() output â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    "ADMIN_FORMAT_BET_TIME_LIMIT": "æŠ•æ³¨æˆªæ­¢æ—¶é—´",
    "ADMIN_FORMAT_TIMEZONE_LINE": "æ—¶åŒºï¼š{tz}",
    "ADMIN_FORMAT_SYSTEM_TIME_ZONE": "ç³»ç»Ÿæ—¶åŒº",
    "ADMIN_FORMAT_CURRENT_LINE": "å½“å‰ï¼š{value}",
    "ADMIN_FORMAT_BONUS_PAYOUT_SETTINGS": "å¥–é‡‘èµ”çŽ‡è®¾ç½®",
    "ADMIN_FORMAT_OVER_LIMIT_SETTINGS": "è¶…é™è®¾ç½®",
    "ADMIN_FORMAT_NOTIFICATIONS": "é€šçŸ¥",
    "ADMIN_FORMAT_CUSTOMER_NOTIF": "å®¢æˆ·é€šçŸ¥ï¼š{status}",
    "ADMIN_FORMAT_OVER_LIMIT_ACTION": "è¶…é™æ“ä½œï¼š{action}",

    # â”€â”€ Bet delete responses â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    "BET_DELETE_NOT_FOUND": "âŒ æœªæ‰¾åˆ°ç¥¨æ®ï¼š{ticket_no}",
    "BET_DELETE_NOT_FOUND_WITH_DATE": "âŒ æœªæ‰¾åˆ°ç¥¨æ®ï¼š{ticket_no}\næ—¥æœŸï¼š{date}",
    "BET_DELETE_ALREADY_DELETED": "âŒ ç¥¨æ®å·²åˆ é™¤ï¼š{ticket_no}",
    "BET_DELETE_ALREADY_DELETED_WITH_DATE": "âŒ ç¥¨æ®å·²åˆ é™¤ï¼š{ticket_no}\næ—¥æœŸï¼š{date}",
    "BET_DELETE_SUCCESS": "ðŸ—‘ å·²åˆ é™¤ Â· {region} Â· {ticket_no}",
    "BET_DELETE_SUCCESS_WITH_DATE": "ðŸ—‘ å·²åˆ é™¤ Â· {region} Â· {ticket_no}\næ—¥æœŸï¼š{date}",

    # â”€â”€ Admin panel menu titles â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    "ADMIN_AGENT_COMM_SETTING": "ä»£ç†ä½£é‡‘è®¾ç½®",
    "ADMIN_OVER_LIMIT_SETTING": "è¶…é™è®¾ç½®",
    "ADMIN_NOTIFICATIONS": "é€šçŸ¥",
    "ADMIN_BET_TIME_LIMIT": "æŠ•æ³¨æˆªæ­¢æ—¶é—´",
    "ADMIN_SYSTEM_TIME_ZONE": "ç³»ç»Ÿæ—¶åŒº",
    "ADMIN_USAGE_DELETE_SLASH": "âŒ ç”¨æ³•ï¼š/delete N1",
    "ADMIN_USAGE_DELETE_TEXT": "âŒ ç”¨æ³•ï¼šdelete N1",

    # â”€â”€ Bet / Other Day menu labels â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    "MENU_OTHER_DAY_INPUT": "å…¶ä»–æ—¥æœŸæŠ•æ³¨",
    "MENU_BET": "æŠ•æ³¨",

    # â”€â”€ Admin panel dynamic templates â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    "ADMIN_AGENT_COMM_CURRENT": "ä»£ç†ä½£é‡‘çŽ‡\n\nå½“å‰ï¼š{rate}%",
    "ADMIN_OVER_LIMIT_CURRENT": "è¶…é™æ“ä½œ\n\nå½“å‰ï¼š{action}",
    "ADMIN_ADDED_USER": "âœ… å·²æ·»åŠ ç®¡ç†å‘˜\nUser IDï¼š{user_id}",
    "ADMIN_AGENT_COMM_UPDATED": "âœ… ä»£ç†ä½£é‡‘å·²æ›´æ–°\nå½“å‰ï¼š{value}%",

    # â”€â”€ Admin panel input validation â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    "ADMIN_INVALID_USER_ID": "âŒ æ— æ•ˆçš„ç”¨æˆ· IDï¼Œè¯·åªè¾“å…¥æ•°å­—ã€‚",
    "ADMIN_INVALID_DATE_FORMAT": "âŒ æ—¥æœŸæ ¼å¼æ— æ•ˆã€‚\nè¯·ä½¿ç”¨ YYYY-MM-DD",
    "ADMIN_ENTER_COMMISSION_RATE": "è¯·è¾“å…¥æ–°çš„ä½£é‡‘çŽ‡ï¼ˆ%ï¼‰ï¼š",
    "ADMIN_BONUS_PAYOUT_SETTING": "å¥–é‡‘èµ”çŽ‡è®¾ç½®",
    "ADMIN_BONUS_PAYOUT_UPDATED": "âœ… å¥–é‡‘èµ”çŽ‡å·²æ›´æ–°",
    "ADMIN_OVER_LIMIT_UPDATED": "âœ… è¶…é™è®¾ç½®å·²æ›´æ–°",
    "ADMIN_CUTOFF_TIME_UPDATED": "âœ… æˆªæ­¢æ—¶é—´å·²æ›´æ–°",
    "ADMIN_SET_ADMIN": "è®¾ç½®ç®¡ç†å‘˜",
    "ADMIN_VIEW_ADMIN_LIST": "æŸ¥çœ‹ç®¡ç†å‘˜åˆ—è¡¨",
    "ADMIN_ADD_ADMIN": "æ·»åŠ ç®¡ç†å‘˜",
    "ADMIN_REMOVE_ADMIN": "ç§»é™¤ç®¡ç†å‘˜",
    "ADMIN_VIEW_CURRENT_AGENT_COMM": "æŸ¥çœ‹å½“å‰ä»£ç†ä½£é‡‘",
    "ADMIN_EDIT_AGENT_COMM": "ç¼–è¾‘ä»£ç†ä½£é‡‘",
    "ADMIN_VIEW_CURRENT_BONUS_PAYOUT": "æŸ¥çœ‹å½“å‰å¥–é‡‘èµ”çŽ‡",
    "ADMIN_EDIT_BONUS_PAYOUT": "ç¼–è¾‘å¥–é‡‘èµ”çŽ‡",
    "ADMIN_VIEW_CURRENT_OVER_LIMIT": "æŸ¥çœ‹å½“å‰è¶…é™è®¾ç½®",
    "ADMIN_EDIT_OVER_LIMIT": "ç¼–è¾‘è¶…é™è®¾ç½®",
    "ADMIN_SET_OVER_LIMIT_ACTION": "è®¾ç½®è¶…é™æ“ä½œ",
    "ADMIN_CONTINUE_ACCEPTING": "ç»§ç»­æŽ¥å—",
    "ADMIN_REJECT_BET": "æ‹’ç»æŠ•æ³¨",
    "ADMIN_VIEW_CURRENT_NOTIFICATION_SETTINGS": "æŸ¥çœ‹å½“å‰é€šçŸ¥è®¾ç½®",
    "ADMIN_ON": "å¼€å¯",
    "ADMIN_OFF": "å…³é—­",
    "ADMIN_VIEW_CURRENT_CUTOFF_TIME": "æŸ¥çœ‹å½“å‰æˆªæ­¢æ—¶é—´",
    "ADMIN_EDIT_CUTOFF_TIME": "ç¼–è¾‘æˆªæ­¢æ—¶é—´",
    "ADMIN_VIEW_CURRENT_TIME_ZONE": "æŸ¥çœ‹å½“å‰æ—¶åŒº",
    "ADMIN_TIMEZONE_KL": "å‰éš†å¡",
    "ADMIN_TIMEZONE_HCM": "èƒ¡å¿—æ˜Žå¸‚",
    "ADMIN_PROMPT_ADD_ADMIN": "è¯·è¾“å…¥è¦æ·»åŠ ä¸ºç®¡ç†å‘˜çš„ Telegram ç”¨æˆ· IDï¼š",
    "ADMIN_PROMPT_REMOVE_ADMIN": "è¯·è¾“å…¥è¦ä»Žç®¡ç†å‘˜ä¸­ç§»é™¤çš„ Telegram ç”¨æˆ· IDï¼š",

    # â”€â”€ Admin panel status confirmations â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    "ADMIN_OVER_LIMIT_SET_ACCEPT": "âœ… è¶…é™æ“ä½œå·²è®¾ä¸ºæŽ¥å—",
    "ADMIN_OVER_LIMIT_SET_REJECT": "âœ… è¶…é™æ“ä½œå·²è®¾ä¸ºæ‹’ç»",
    "ADMIN_NOTIF_SET_ON": "âœ… å®¢æˆ·é€šçŸ¥å·²å¼€å¯",
    "ADMIN_NOTIF_SET_OFF": "âœ… å®¢æˆ·é€šçŸ¥å·²å…³é—­",
    "ADMIN_TIMEZONE_SET_KL": "âœ… ç³»ç»Ÿæ—¶åŒºå·²è®¾ä¸º Asia/Kuala_Lumpur",
    "ADMIN_TIMEZONE_SET_HCM": "âœ… ç³»ç»Ÿæ—¶åŒºå·²è®¾ä¸º Asia/Ho_Chi_Minh",

    # â”€â”€ Report menu handler â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    "REPORT_OVER_LIMIT_TITLE": "âš ï¸ è¶…é™æŠ¥è¡¨",
    "REPORT_SELECT_TYPE_TITLE": "ðŸ“Š é€‰æ‹©æŠ¥è¡¨ç±»åž‹",
    "REPORT_GENERATE_FAILED": "âŒ æŠ¥è¡¨ç”Ÿæˆå¤±è´¥ï¼š{error}",

    # â”€â”€ Report labels (menu layer) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    "REPORT_MENU_TITLE": "æŠ¥è¡¨",
    "REPORT_LABEL_TRANSACTION": "äº¤æ˜“è®°å½•",
    "REPORT_LABEL_SETTLEMENT": "ç»“ç®—",
    "REPORT_LABEL_NUMBER_DETAIL": "å·ç æ˜Žç»†",
    "REPORT_LABEL_OVER_LIMIT": "è¶…é¢",
    "REPORT_COMING_SOON": "å³å°†æŽ¨å‡º",
    "REPORT_NO_DATA": "æ— å¯ç”¨æ•°æ®ã€‚",

    # â”€â”€ Shared table column headers (bet + report formatters) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    "COL_REGION": "åœ°åŒº",
    "COL_NUMBER": "å·ç ",
    "COL_MODE": "çŽ©æ³•",
    "COL_TOTAL": "åˆè®¡",
    "COL_BET": "æŠ•æ³¨",
    "COL_WIN": "ä¸­å¥–",

    # â”€â”€ Bet formatter â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    "BET_ACCEPTED": "âœ… æŠ•æ³¨æˆåŠŸ",
    "BET_TOTAL_LINE": "ðŸ’° åˆè®¡ï¼š{value}",
    "BET_INVALID_INPUT": "æ— æ•ˆè¾“å…¥",
    "BET_SCHEDULE_CLOSED": "æ‰€é€‰æ—¥æœŸè¯¥åœ°åŒºæœªå¼€æ”¾",

    # â”€â”€ Bet service â€” test mode â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    "BET_TEST_MODE_NOTICE": "âš  æµ‹è¯•æ¨¡å¼ Â· ç®¡ç†å‘˜å¯æŠ•æ³¨åŽ†å²æ—¥æœŸ",

    # â”€â”€ Bet service â€” over-limit notification â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    "BET_OVER_LIMIT_ACCEPT": "âš ï¸ å·²è¶…é™\nç»§ç»­æŽ¥å—",
    "BET_OVER_LIMIT_REJECT": "âš ï¸ å·²è¶…é™\næ‹’ç»æŠ•æ³¨",
    "BET_OVER_LIMIT_INPUT": "è¾“å…¥ï¼š{value}",

    # â”€â”€ Bet service â€” cutoff closed â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    "BET_CUTOFF_CLOSED": "âš ï¸ æŠ•æ³¨å·²æˆªæ­¢",
    "BET_CUTOFF_REGION_TIME": "{region} æˆªæ­¢äºŽ {time}",

    # â”€â”€ Result formatter â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    "RESULT_TITLE": "ðŸ“Š å¼€å¥–ç»“æžœ",
    "RESULT_DATE_LABEL": "ðŸ“… æ—¥æœŸï¼š",
    "RESULT_NOT_AVAILABLE": "ç»“æžœæš‚æœªå…¬å¸ƒã€‚",
    "RESULT_FETCHED_LABEL": "ðŸ•’ èŽ·å–æ—¶é—´ï¼š",

    # â”€â”€ Report formatters (body text) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    "REPORT_TRANSACTION_TITLE": "ðŸ“Š äº¤æ˜“æŠ¥è¡¨",
    "REPORT_SETTLEMENT_TITLE": "ðŸ“˜ ç»“ç®—æŠ¥è¡¨",
    "REPORT_NUMBER_DETAIL_TITLE": "ðŸ”¢ å·ç æ˜Žç»†æŠ¥è¡¨",
    "REPORT_DATE_LABEL": "æ—¥æœŸï¼š{date}",
    "REPORT_REGION_NO_DATA": "æ— æ•°æ®",
    "REPORT_TICKET_NO_DETAIL": "æ— æ˜Žç»†",
    "REPORT_TICKET_TOTAL": "ç¥¨æ®åˆè®¡ï¼š{value}",
    "REPORT_TICKET_WIN": "ç¥¨æ®ä¸­å¥–ï¼š{value}",
    "REPORT_BET_TOTAL": "æŠ•æ³¨åˆè®¡",
    "REPORT_PAYOUT": "æ´¾å½©",
    "REPORT_AGENT_COMM": "ä»£ç†ä½£é‡‘",
    "REPORT_REGION_SETTLEMENT": "{region} ç»“ç®—",
    "REPORT_TOTAL_SETTLEMENT": "æ€»ç»“ç®—",
    "REPORT_WINNING_DETAILS": "ä¸­å¥–æ˜Žç»†",
    "REPORT_NO_WINNING": "æ— ä¸­å¥–è®°å½•",
    "REPORT_GENERATED_AT": "ðŸ•’ ç”Ÿæˆæ—¶é—´ï¼š{ts}ï¼ˆUTC+8ï¼‰",
    "REPORT_TOO_MANY_RECORDS": "âš ï¸ è®°å½•è¿‡å¤šï¼š{tickets} å¼ ç¥¨ï¼Œ{lines} è¡Œ",
    "REPORT_USE_EXPORT": "ðŸ“„ è¯·ä½¿ç”¨å¯¼å‡º HTML æŸ¥çœ‹å®Œæ•´æŠ¥è¡¨",
    "REPORT_REGION_SUMMARY": "📍 {region}：{tickets} 张票，{lines} 行，合计：{total}",
    "REPORT_NUMBER_ENTRY_SUMMARY": "{region}：{count} 条号码记录",
    "REPORT_TRUNCATED": "ðŸ“ æŠ¥è¡¨å› é•¿åº¦é™åˆ¶è¢«æˆªæ–­",
    "BOT_SCOPE_PRIVATE_ONLY": "此机器人仅限指定群组内使用",
    "BOT_SCOPE_UNAUTHORIZED_GROUP": "此机器人未授权在本群使用",
    # â”€â”€ Telegram command menu descriptions â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    "CMD_START":      "ä¸»èœå•",
    "CMD_MN":         "æŠ•æ³¨å—éƒ¨ï¼ˆä»Šæ—¥ï¼‰",
    "CMD_MT":         "æŠ•æ³¨ä¸­éƒ¨ï¼ˆä»Šæ—¥ï¼‰",
    "CMD_MB":         "æŠ•æ³¨åŒ—éƒ¨ï¼ˆä»Šæ—¥ï¼‰",
    "CMD_SETTLEMENT": "ä»Šæ—¥ç»“ç®—æŠ¥å‘Š",
}

