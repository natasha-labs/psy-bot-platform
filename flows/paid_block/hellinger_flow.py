from telegram import InlineKeyboardMarkup, InlineKeyboardButton


# ================= STATE =================

def reset_state(context):
    context.user_data["hellinger"] = {
        "stage": "intro"
    }


def get_state(context):
    return context.user_data.get("hellinger", {})


# ================= KEYBOARDS =================

def kb_start():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Перейти к практике", callback_data="h_start")]
    ])


def kb_begin():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Начать", callback_data="h_begin")]
    ])


def kb_theme():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Деньги", callback_data="h_theme_money")],
        [InlineKeyboardButton("Отношения", callback_data="h_theme_rel")],
        [InlineKeyboardButton("Ситуация", callback_data="h_theme_sit")],
    ])


def kb_touch():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Дотронулся(лась)", callback_data="h_touch")]
    ])


def kb_reaction():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Есть реакция", callback_data="h_react_yes")],
        [InlineKeyboardButton("Ничего не меняется", callback_data="h_react_no")],
    ])


def kb_move():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Есть реакция", callback_data="h_react_yes")],
        [InlineKeyboardButton("Ничего не меняется", callback_data="h_react_no")],
        [InlineKeyboardButton("Хочу завершить", callback_data="h_finish")],
    ])


def kb_stop():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Есть реакция", callback_data="h_react_yes")],
        [InlineKeyboardButton("Хочу завершить", callback_data="h_finish")],
    ])


def kb_finish():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Выйти в меню", callback_data="h_exit")]
    ])


# ================= ENTRY =================

async def send_hellinger_entry(update, context):
    reset_state(context)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            "Это не тест и не теория.\n"
            "Это практика, где ты смотришь на свою ситуацию.\n"
            "Здесь нет правильных ответов.\n"
            "Важно только смотреть, что происходит.\n"
            "Иногда может быть пусто или непонятно. Это нормально.\n\n"
            "Если ты не знаком(а) с расстановками — лучше сначала посмотреть видео о том как проходят расстановки.
          
        ),
        reply_markup=kb_start(),
    )


# ================= FLOW =================

async def handle_hellinger_callback(update, context):
    query = update.callback_query
    data = query.data

    try:
        await query.edit_message_reply_markup(None)
    except:
        pass

    chat_id = update.effective_chat.id

    # вход
    if data == "h_start":
        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                "Это практика через предметы.\n"
                "Каждый предмет — это фигура.\n"
                "Подготовь 5–10 предметов.\n"
                "Ставь их так, как ощущается.\n\n"
                "Касание = вход\n"
                "Убрал руку = выход\n"
                "Можно двигать.\n"
                "Можно добавлять.\n\n"
                "Не нужно ничего специально чувствовать. Просто смотри."
            ),
            reply_markup=kb_begin(),
        )
        return True

    # тема
    if data == "h_begin":
        await context.bot.send_message(
            chat_id=chat_id,
            text="С чем хочешь поработать?",
            reply_markup=kb_theme(),
        )
        return True

    # постановка
    if data.startswith("h_theme_"):
        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                "Поставь в поле:\n"
                "— себя\n"
                "— вторую фигуру\n\n"
                "Не спеши.\n"
                "Просто смотри."
            ),
        )

        await context.bot.send_message(
            chat_id=chat_id,
            text="Когда будешь готов(а) — дотронься до фигуры",
            reply_markup=kb_touch(),
        )
        return True

    # считывание
    if data == "h_touch":
        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                "Дотронься и смотри, что появляется\n\n"
                "мысль\nощущение\nжелание"
            ),
            reply_markup=kb_reaction(),
        )
        return True

    # есть реакция → движение
    if data == "h_react_yes":
        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                "Если хочется изменить — сделай это\n\n"
                "двигай\nприближай\nотдаляй\n\n"
                "Если есть напряжение —\n"
                "можно вынести в отдельную фигуру"
            ),
            reply_markup=kb_move(),
        )
        return True

    # нет реакции
    if data == "h_react_no":
        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                "Это часть процесса\n\n"
                "Можно просто смотреть\n"
                "или дотронуться до другой фигуры"
            ),
            reply_markup=kb_stop(),
        )
        return True

    # завершение
    if data == "h_finish":
        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                "Посмотри на поле\n\n"
                "Как стоят фигуры\n"
                "Что между ними\n\n"
                "Это текущая картина"
            ),
            reply_markup=kb_finish(),
        )
        return True

    # выход
    if data == "h_exit":
        from flows.paid_block.paid_space_flow import send_space_menu_text
        await send_space_menu_text(update, context)
        return True

    return False
