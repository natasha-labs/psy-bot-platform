from telegram import ReplyKeyboardMarkup

ADMIN_ID = 5750354905

SPACE_TOOL_NAMES = {
    "🌿 Расстановки (Берт Хеллингер)",
    "🃏 Метафорические карты (МАК)",
    "⚖️ Колесо баланса",
    "🔺 Роли в отношениях (Треугольник Карпмана)",
    "🧠 Схематерапия (Джеффри Янг)",
    "🎭 Внутренние семейные системы IFS (Ричард Шварц)",
}


def is_admin(user_id) -> bool:
    return str(user_id) == str(ADMIN_ID)


def get_space_menu_keyboard(user_id=None):
    rows = [
        ["🌿 Расстановки (Берт Хеллингер)", "🃏 Метафорические карты (МАК)"],
        ["🎭 Внутренние семейные системы IFS (Ричард Шварц)", "⚖️ Колесо баланса"],
        ["🔺 Роли в отношениях (Треугольник Карпмана)", "🧠 Схематерапия (Джеффри Янг)"],
        ["ℹ️ О пространстве", "🔄 Назад"],
    ]

    if user_id is not None and is_admin(user_id):
        rows.append(["Сбросить мои тесты", "QA: открыть пространство"])
        rows.append(["Выдать платный доступ", "Забрать платный доступ"])

    return ReplyKeyboardMarkup(rows, resize_keyboard=True)


def is_space_tool_text(text: str) -> bool:
    return text in SPACE_TOOL_NAMES


async def send_space_menu_text(update, context):
    user = update.effective_user
    user_id = user.id if user else None

    await update.message.reply_text(
        "Выбери, с чем хочешь поработать сегодня:",
        reply_markup=get_space_menu_keyboard(user_id),
    )


async def send_about_space(update, context):
    user = update.effective_user
    user_id = user.id if user else None

    text = (
        "Привет. Меня зовут Наташа.\n\n"
        "Я психолог и работаю в интегративном подходе. Это значит, что я не разделяю методы, а соединяю их — чтобы видеть человека целостно и работать глубже.\n\n"
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
        "Здесь можно быть в контакте с собой каждый день. Потому что жизнь — это исследование себя.\n\n"
        "Это пространство создано для твоего самопознания, в которое можно возвращаться снова и снова."
    )

    await update.message.reply_text(
        text,
        reply_markup=get_space_menu_keyboard(user_id),
    )


async def send_tool_stub(update, context, tool_name: str):
    user = update.effective_user
    user_id = user.id if user else None

    # 👇 ВАЖНО: МАК не должен идти в stub
    if tool_name == "🃏 Метафорические карты (МАК)":
        from flows.paid_block.mak_flow import send_mak_entry
        await send_mak_entry(update, context)
        return

    text = (
        f"{tool_name}\n\n"
        "Этот инструмент сейчас в разработке.\n"
        "Он скоро станет доступен."
    )

    await update.message.reply_text(
        text,
        reply_markup=get_space_menu_keyboard(user_id),
    )
