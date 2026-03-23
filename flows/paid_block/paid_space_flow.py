from telegram import InlineKeyboardMarkup, InlineKeyboardButton


# ====== КНОПКИ ======

def entry_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👉 Перейти в пространство", callback_data="paid_space_entry")]
    ])


def about_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Начать", callback_data="paid_space_menu")]
    ])


def menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🌿 Расстановка (Хеллингер)", callback_data="tool_hellinger")],
        [InlineKeyboardButton("🃏 Метафорические карты", callback_data="tool_mac")],
        [InlineKeyboardButton("🔮 Таро", callback_data="tool_taro")],
        [InlineKeyboardButton("⚖️ Колесо баланса", callback_data="tool_balance")],
        [InlineKeyboardButton("🔺 Роли в отношениях", callback_data="tool_roles")],
        [InlineKeyboardButton("🧠 Схемотерапия", callback_data="tool_schema")],
        [InlineKeyboardButton("🎭 Внутренний диалог", callback_data="tool_ifs")],
        [InlineKeyboardButton("ℹ️ О пространстве", callback_data="about_space")],
        [InlineKeyboardButton("🔄 Вернуться назад", callback_data="back_to_space")],
    ])


def back_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Вернуться в пространство", callback_data="paid_space_menu")]
    ])


# ====== ЭКРАНЫ ======

async def send_entry_screen(update, context):
    text = (
        "Ты внутри.\n\n"
        "Теперь у тебя есть доступ к пространству самопознания.\n\n"
        "Здесь ты можешь исследовать себя разными способами:\n"
        "— через практику\n"
        "— через образы\n"
        "— через расклады\n"
        "— через внутренние состояния\n\n"
        "👉 Выбери, с чего начать сегодня."
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=entry_keyboard(),
    )


async def send_about_screen(update, context):
    text = (
        "Привет. Меня зовут Наташа.\n\n"
        "Я психолог и работаю в интегративном подходе.\n"
        "Это значит, что я не разделяю методы, а соединяю их — чтобы видеть человека целостно и работать глубже.\n\n"
        "Тебе не нужно больше бегать по разным специалистам в поисках ответов.\n\n"
        "Я собрала в одном месте инструменты, через которые ты можешь увидеть:\n"
        "1. что с тобой происходит;\n"
        "2. почему это повторяется;\n"
        "3. где ты теряешь себя;\n"
        "4. куда уходит твоя энергия;\n"
        "5. как начать это менять.\n\n"
        "Сначала ты проходишь быстрый вход и видишь базовую картину.\n\n"
        "А дальше открывается пространство глубже:\n"
        "— практики\n"
        "— родовые темы\n"
        "— образы\n"
        "— схемы\n"
        "— роли\n"
        "— внутренние части\n\n"
        "Здесь можно быть в контакте с собой каждый день.\n"
        "Потому что жизнь — это исследование себя.\n\n"
        "Это пространство создано для твоего самопознания,\n"
        "в которое можно возвращаться снова и снова."
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=about_keyboard(),
    )


async def send_menu(update, context):
    text = "Выбери, с чем хочешь поработать сегодня:"

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=menu_keyboard(),
    )


async def send_tool_stub(update, context):
    text = (
        "Этот инструмент сейчас в разработке.\n\n"
        "Он скоро станет доступен."
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=back_keyboard(),
    )
