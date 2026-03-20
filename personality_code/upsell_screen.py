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
            [InlineKeyboardButton("Разобрать глубже", callback_data="full_profile_info")]
        ]
    )


def get_payment_placeholder_text():
    return (
        "Вы уже увидели базовый профиль.\n\n"
        "Но это только верхний слой.\n\n"
        "Глубже находятся:\n"
        "— скрытые паттерны\n"
        "— внутренние конфликты\n"
        "— реальные причины ваших реакций"
    )
