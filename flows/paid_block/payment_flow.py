from flows.paid_block.paid_access import grant_paid_access

async def send_payment(update, context):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Оплата тестовая (эмуляция)"
    )

async def handle_payment_success(update, context):
    user_id = update.effective_user.id
    grant_paid_access(user_id)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Оплата прошла. Доступ открыт."
    )
