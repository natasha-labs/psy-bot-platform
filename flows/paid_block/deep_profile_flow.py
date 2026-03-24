from flows.paid_block.paid_space_flow import (
    send_about_space,
    send_space_menu_text,
    send_tool_stub,
)


TOOL_LABELS = {
    "tool_hellinger": "🌿 Расстановки (Берт Хеллингер)",
    "tool_mac": "🃏 Метафорические карты (МАК)",
    "tool_taro": "🔮 ТАРО (полный расклад)",
    "tool_balance": "⚖️ Колесо баланса",
    "tool_roles": "🔺 Роли в отношениях (Треугольник Карпмана)",
    "tool_schema": "🧠 Схематерапия (Джеффри Янг)",
    "tool_ifs": "🎭 Внутренние семейные системы IFS (Ричард Шварц)",
}


async def handle_paid_callback(update, context):
    query = update.callback_query
    if not query:
        return

    data = query.data

    if data == "open_space":
        await send_space_menu_text(update, context)
        return

    if data == "paid_space_entry":
        await send_about_space(update, context)
        return

    if data == "paid_space_menu":
        await send_space_menu_text(update, context)
        return

    if data == "about_space":
        await send_about_space(update, context)
        return

    if data == "back_to_space":
        await send_space_menu_text(update, context)
        return

    if data in TOOL_LABELS:
        await send_tool_stub(update, context, TOOL_LABELS[data])
        return
