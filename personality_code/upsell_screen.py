from telegram import InlineKeyboardMarkup, InlineKeyboardButton


def get_deep_dive_keyboard():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Получить полный код личности", callback_data="full_profile_info")]
        ]
    )


def get_full_profile_keyboard():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Получить полный код личности", callback_data="full_profile_info")]
        ]
    )


def get_payment_placeholder_text():
    return (
        "Ты уже увидел верхний слой своих реакций.\n\n"
        "Но он не объясняет:\n"
        "— почему ты так реагируешь\n"
        "— где формируется напряжение\n"
        "— что на самом деле тобой управляет\n\n"
        "Сейчас мы разберём это глубже."
    )
