from telegram import InlineKeyboardMarkup, InlineKeyboardButton


def get_deep_dive_keyboard():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Разобрать глубже", callback_data="full_profile_info")]
        ]
    )


def get_full_profile_keyboard():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Открыть полный код личности", callback_data="full_profile_info")]
        ]
    )


def get_payment_placeholder_text():
    return (
        "🔒 *Полный разбор скоро будет подключён к оплате.*\n\n"
        "Здесь появится платная версия,\n"
        "в которой можно будет получить\n"
        "глубокий персональный разбор."
    )
