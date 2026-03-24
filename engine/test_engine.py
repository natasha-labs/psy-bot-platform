from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
)


async def send_entry_screen(update, context, main_menu_markup):
    text = (
        "Ты думаешь, что понимаешь себя.\n\n"
        "Но решения, реакции и выборы часто происходят автоматически.\n\n"
        "Внутри тебя есть система, которая управляет этим:\n"
        "— как ты реагируешь\n"
        "— что чувствуешь\n"
        "— какие сценарии повторяешь\n\n"
        "Мы собрали короткие тесты, которые покажут твой внутренний код.\n\n"
        "Это займёт 2–3 минуты.\n\n"
        "Выбери, с чего начать:"
    )

    keyboard = [
        ["Тревога"],
        ["Архетип личности"],
        ["Теневой профиль"],
    ]

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup)
    elif update.callback_query:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            reply_markup=reply_markup,
        )
