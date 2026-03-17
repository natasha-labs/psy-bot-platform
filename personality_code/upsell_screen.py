from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from personality_code.renderer import render_upsell_text


def get_upsell_text():
    return render_upsell_text()


def get_upsell_keyboard():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Открыть полный код личности",
                    callback_data="full_profile_info",
                )
            ]
        ]
    )


def get_full_profile_info_text():
    return (
        "🔒 *ПОЛНЫЙ ПРОФИЛЬ ЛИЧНОСТИ*\n\n"
        "Полный профиль пока находится в разработке.\n\n"
        "Скоро здесь появится расширенная версия системы «Код личности» "
        "с дополнительными тестами и более глубокой интерпретацией."
    )
