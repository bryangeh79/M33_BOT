# ONLY PATCH SECTION SHOWN

def _build_admin_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("1. Customer Setting", callback_data="admin_customer_menu")],
        [InlineKeyboardButton("2. Agent Comm Setting", callback_data=CALLBACK_ADMIN_AGENT_MENU)],
        [InlineKeyboardButton("3. Bonus Payout Setting", callback_data=CALLBACK_ADMIN_BONUS_MENU)],
        [InlineKeyboardButton("4. Over Limit Setting", callback_data=CALLBACK_ADMIN_LIMIT_MENU)],
        [InlineKeyboardButton("5. System Setting", callback_data="admin_system_setting_menu")],
        [InlineKeyboardButton("❌ Close", callback_data=CALLBACK_ADMIN_CLOSE)],
    ]
    return InlineKeyboardMarkup(keyboard)


def _build_customer_setting_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("Add Customer", callback_data="admin_customer_add")],
        [InlineKeyboardButton("Delete Customer", callback_data="admin_customer_delete")],
        [InlineKeyboardButton("View Customer List", callback_data="admin_customer_list")],
        [InlineKeyboardButton("⬅ Back", callback_data=CALLBACK_ADMIN_BACK)],
    ]
    return InlineKeyboardMarkup(keyboard)


def _build_system_setting_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("Notifications", callback_data=CALLBACK_ADMIN_NOTIFICATIONS_MENU)],
        [InlineKeyboardButton("Set Admin", callback_data=CALLBACK_ADMIN_SET_ADMIN)],
        [InlineKeyboardButton("System Time Zone", callback_data=CALLBACK_ADMIN_SYSTEM_TZ_MENU)],
        [InlineKeyboardButton("⬅ Back", callback_data=CALLBACK_ADMIN_BACK)],
    ]
    return InlineKeyboardMarkup(keyboard)
