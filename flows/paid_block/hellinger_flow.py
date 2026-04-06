from telegram import InlineKeyboardMarkup, InlineKeyboardButton


def reset_state(context):
    context.user_data["hellinger"] = {
        "stage": "intro",
        "theme": None
    }


def kb_start():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Начать", callback_data="h_start")]
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


async def send_hellinger_entry(update, context):
    reset_state(context)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            "Если ты никогда не работал(а) с такими практиками —\n"
            "начни с техники «Род».\n\n"
            "Она проще и помогает понять сам процесс:\n"
            "как работать с предметами,\n"
            "как замечать реакции,\n"
            "как «считывать», что происходит в поле.\n\n"
            "После неё будет гораздо легче работать в этой практике.\n\n"
            "⸻\n\n"
            "Это практика, где ты смотришь на свою ситуацию через предметы.\n\n"
            "Каждый предмет на время становится фигурой —\n"
            "он обозначает часть твоей ситуации:\n"
            "тебя, другого человека, деньги, событие или состояние.\n\n"
            "⸻\n\n"
            "Поле — это место, где проходит практика.\n"
            "Это может быть лист бумаги, стол или участок пола.\n"
            "Все предметы находятся внутри этого поля.\n\n"
            "⸻\n\n"
            "Подойдут любые небольшие предметы:\n"
            "камни, ручки, флаконы, статуэтки и т.д.\n"
            "Подготовь 5–10 предметов.\n"
            "Один предмет = одна роль.\n\n"
            "⸻\n\n"
            "Ты ставишь предметы так, как это ощущается сейчас.\n"
            "Как поставил(а) — так сейчас и выглядит ситуация.\n\n"
            "⸻\n\n"
            "Когда ты касаешься предмета —\n"
            "смотришь на ситуацию как будто «из него».\n\n"
            "Когда убираешь руку —\n"
            "взаимодействие заканчивается.\n\n"
            "⸻\n\n"
            "Если хочется двигать предметы — двигай.\n"
            "Если появляется что-то ещё — добавляй новую фигуру.\n\n"
            "Если непонятно, что это —\n"
            "дотронься и задай вопрос:\n"
            "«кто ты?» или «что ты?»\n\n"
            "⸻\n\n"
            "Не нужно специально что-то чувствовать.\n"
            "Есть реакция — смотри.\n"
            "Нет — просто наблюдай.\n\n"
            "⸻\n\n"
            "После практики не обязательно сразу убирать поле.\n"
            "Иногда важно оставить всё как есть,\n"
            "чтобы процесс «доработался».\n\n"
            "⸻\n\n"
            "МИНИ-ПРИМЕР:\n\n"
            "ты ставишь в поле себя и деньги\n\n"
            "смотришь на них несколько секунд\n"
            "отмечаешь расстояние и состояние\n\n"
            "⸻\n\n"
            "дотрагиваешься до себя\n\n"
            "смотришь, что появляется\n"
            "мысль, ощущение или желание\n\n"
            "можно задать вопрос:\n"
            "как я отношусь к деньгам\n"
            "могу ли я подойти\n"
            "могу ли взять\n\n"
            "⸻\n\n"
            "если есть ощущение «не могу» —\n"
            "значит в поле есть ещё что-то\n\n"
            "можно поставить новую фигуру и посмотреть\n\n"
            "⸻\n\n"
            "дотрагиваешься до денег\n\n"
            "смотришь: есть ли движение к тебе или от тебя\n\n"
            "⸻\n\n"
            "дальше просто продолжаешь процесс"
        ),
        reply_markup=kb_start(),
    )


async def handle_hellinger_callback(update, context):
    query = update.callback_query
    data = query.data

    try:
        await query.edit_message_reply_markup(None)
    except:
        pass

    chat_id = update.effective_chat.id
    state = context.user_data.get("hellinger", {})

    if data == "h_start":
        await context.bot.send_message(
            chat_id=chat_id,
            text="С чем хочешь поработать?",
            reply_markup=kb_theme(),
        )
        return True

    if data.startswith("h_theme_"):
        state["theme"] = data

        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                "Поставь в поле:\n"
                "— себя\n"
                "— вторую фигуру\n\n"
                "Не спеши.\n"
                "Просто посмотри на них."
            ),
        )

        await context.bot.send_message(
            chat_id=chat_id,
            text="Когда будешь готов(а) — дотронься до любой фигуры.",
            reply_markup=kb_touch(),
        )
        return True

    if data == "h_touch":
        theme = state.get("theme")

        text = (
            "Дотронься до фигуры\n"
            "и посмотри, что появляется.\n\n"
            "Это может быть:\n"
            "мысль, ощущение или желание что-то сделать."
        )

        if theme == "h_theme_money":
            text += "\n\n— как я отношусь к деньгам\n— могу ли подойти\n— могу ли взять"

        if theme == "h_theme_rel":
            text += "\n\n— как я отношусь к партнёру\n— есть ли движение\n— что между вами"

        if theme == "h_theme_sit":
            text += "\n\n— как я к этому отношусь\n— могу ли приблизиться\n— что происходит между вами"

        await context.bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=kb_reaction(),
        )
        return True

    if data == "h_react_yes":
        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                "Если хочется что-то изменить — сделай это.\n\n"
                "Можно:\n"
                "двигать\nприближать\nотдалять\nповорачивать"
            ),
        )

        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                "Если появляется напряжение или тяжесть —\n"
                "можно вынести это в отдельную фигуру."
            ),
            reply_markup=kb_move(),
        )
        return True

    if data == "h_react_no":
        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                "Это тоже часть процесса.\n\n"
                "Можно просто побыть в этом\n"
                "или дотронуться до другой фигуры."
            ),
            reply_markup=kb_stop(),
        )
        return True

    if data == "h_finish":
        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                "Посмотри, что сейчас в поле.\n\n"
                "Как стоят фигуры.\n"
                "Что между ними происходит.\n\n"
                "Это и есть текущая картина процесса."
            ),
            reply_markup=kb_finish(),
        )
        return True

    if data == "h_exit":
        from flows.paid_block.paid_space_flow import send_space_menu_text
        await send_space_menu_text(update, context)
        return True

    return False


async def handle_hellinger_text(update, context):
    text = update.message.text.lower()

    if "деньги ушли" in text:
        await update.message.reply_text(
            "Ты видишь, что деньги вышли из поля.\nПосмотри, что сейчас происходит с остальными фигурами."
        )
        return True

    if "ничего не чувствую" in text:
        await update.message.reply_text(
            "Это нормально.\nМожно просто смотреть или дотронуться до другой фигуры."
        )
        return True

    if "не хочу" in text:
        await update.message.reply_text(
            "Это тоже часть процесса.\nМожно это не менять и просто посмотреть."
        )
        return True

    return False
