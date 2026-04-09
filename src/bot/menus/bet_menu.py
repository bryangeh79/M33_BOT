from telegram import ReplyKeyboardMarkup

# 定义 Bet 菜单按钮
BET_MENU_BUTTONS = [["MN", "MT", "MB"]]

def get_bet_menu_keyboard():
    return ReplyKeyboardMarkup(BET_MENU_BUTTONS, one_time_keyboard=True, resize_keyboard=True)