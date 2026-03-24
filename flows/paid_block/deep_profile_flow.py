from flows.paid_block.paid_space_flow import (
    send_about_space,
    send_space_menu_text,
    send_tool_stub,
)


async def handle_paid_callback(update, context):
    query = update.callback_query
    if not query:
        return

    data = query.data

    if data == "open_space":
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Выбери, с чем хочешь поработать сегодня:",
            reply_markup=None,
        )
        return

    if data == "paid_space_entry":
        await send_about_space(update, context)
        return

    if data == "paid_space_menu":
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Выбери, с чем хочешь поработать сегодня:",
        )
        return

    if data == "about_space":
        await send_about_space(update, context)
        return

    if data == "back_to_space":
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Выбери, с чем хочешь поработать сегодня:",
        )
        return

    if data.startswith("tool_"):
        await send_tool_stub(update, context, data)
        return
