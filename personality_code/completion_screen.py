from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from personality_code.renderer import render_basic_code_ready_text


def get_completion_text():
    return render_basic_code_ready_text()


def get_completion_keyboard():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Получить код личности",
                    callback_data="show_basic_code",
                )
            ]
        ]
    )
