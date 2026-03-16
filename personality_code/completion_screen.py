from telegram import InlineKeyboardMarkup, InlineKeyboardButton


def completion_text():
    return (
        "✨ *Ваш базовый код личности готов*\n\n"

        "На основе трёх тестов мы собрали\n"
        "ваш начальный психологический профиль.\n\n"

        "Он показывает:\n\n"

        "• как вы проявляетесь в мире\n"
        "• какие реакции скрыты\n"
        "• что влияет на ваши решения"
    )


def completion_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Получить код личности", callback_data="show_personality_code")]
    ])
