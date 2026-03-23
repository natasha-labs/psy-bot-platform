from telegram import InlineKeyboardMarkup, InlineKeyboardButton

async def send_paid_entry(update, context):
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Начать углублённый разбор", callback_data="paid_start")]]
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Сейчас мы разберём это глубже.",
        reply_markup=keyboard
    )
