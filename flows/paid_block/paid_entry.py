from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from flows.paid_block.paid_access import has_paid_access


def get_paid_entry_keyboard():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Начать второй этап", callback_data="paid_start_deep_profile")]
        ]
    )


async def send_paid_entry(update, context):
    user = update.effective_user
    user_id = user.id if user else "unknown"

    if not has_paid_access(user_id):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=(
                "Вы уже увидели базовый профиль.\n\n"
                "Но это только верхний слой.\n\n"
                "Глубже находятся скрытые паттерны, внутренние конфликты "
                "и реальные причины реакций."
            ),
        )
        return

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            "Второй этап диагностики открыт.\n\n"
            "Сейчас будет уточнение профиля через дополнительные вопросы.\n"
            "Нужно ответить ещё на 10–12 вопросов."
        ),
        reply_markup=get_paid_entry_keyboard(),
    )
