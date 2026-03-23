from flows.paid_block.paid_space_flow import (
    send_entry_screen,
    send_about_screen,
    send_menu,
    send_tool_stub,
)


async def handle_paid_callback(update, context):
    query = update.callback_query
    data = query.data

    if data == "paid_space_entry":
        await send_about_screen(update, context)
        return

    if data == "paid_space_menu":
        await send_menu(update, context)
        return

    if data == "about_space":
        await send_about_screen(update, context)
        return

    if data == "back_to_space":
        await send_menu(update, context)
        return

    if data.startswith("tool_"):
        await send_tool_stub(update, context)
        return
