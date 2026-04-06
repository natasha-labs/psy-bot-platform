from telegram import InlineKeyboardMarkup, InlineKeyboardButton


ROD_PRACTICE_TEXT = """Практика «Род»

Это самостоятельная практика в стиле расстановки по Хеллингеру.
Её лучше проходить спокойно, без спешки, в одиночестве, когда тебя никто не отвлекает.

Если ты проходишь её впервые, просто читай текст медленно и делай то, что откликается внутри.
Здесь не нужно ничего делать правильно.
Важно только идти за текстом и замечать, что происходит в теле, чувствах, мыслях и образах.

Сядь или встань так, чтобы тебе было удобно и можно было почувствовать опору под ягодицами или ногами.
Можно прикрыть глаза.

Представь птицу рода, которую образуют все предки, стоящие за твоей спиной.
За левым плечом стоит мама, за правым — папа.
Даже если ты их никогда не видел(а), их фигуры есть.
За их плечами — их родители, и так далее до седьмого колена.
Все члены рода находятся позади тебя.

Внимательно прислушайся к ощущениям и инстинктам в теле, к чувствам и эмоциям, а также к мыслям и убеждениям, которые возникают.

Это могут быть разные телесные реакции:
сжаться, кричать, бежать, застыть, окаменеть.
У тебя могут быть и другие реакции.
Признай всё, что есть.

Я признаю весь опыт, связанный с этими желаниями,
и то, как эти инстинкты поддерживали мою безопасность.
Я признаю всех предков, которые проживали подобный опыт,
и все истории, которые есть в моём роду.
Я признаю все незавершённые истории.
И я признаю, что эти истории закончились.

Я также признаю весь опыт моей души, связанный с этими реакциями.
Они есть во мне, но я больше их.

Я благодарю эти инстинкты и отпускаю.
Теперь я могу отпустить это
и быть в безопасности.

Если поднимаются чувства и эмоции — ужас, страх, скорбь, горечь, злость или что-то другое —
признай и их тоже.

Я признаю всех предков
и все незавершённые истории, которые есть в моём роду.
Я признаю их с уважением к вашей судьбе.
Вы справились.
Всё закончилось.
Вы можете быть спокойны.
Сейчас другое время.
Я это признаю и отпускаю.

Возможно, я буду первой(ым) из вас,
кто проживёт эту жизнь по-другому.

Я признаю опыт моей души, связанный с этими чувствами.
Этот опыт не был напрасным.
Я признаю ценность и важность всех своих опытов и всех своих уроков.
Я иду дальше.

Если приходят мысли, идеи, убеждения —
не спорь с ними, просто признай их.

Я признаю весь опыт предков
и их послания, которые я усвоил(а), осознанно или нет.
Но сейчас другое время.
И я возвращаю это вам
с благодарностью за жизнь.
Вы справились, значит и я смогу.
Из уважения к вам
я сделаю со своей жизнью что-то хорошее.

Я признаю весь опыт своей души,
связанный с этим убеждением,
все сценарии, чувства и мысли, в которых я застрял(а).
Но сейчас эти идеи, убеждения и мыслеформы
я отменяю, отменяю, отменяю.

Затем снова представь птицу рода.

За правым плечом — всех мужчин рода.
Я женщина (мужчина) нашего рода.
Я одна (один) из вас.
Прямо сейчас я готова(готов) принять в дар ваше благословение.

За левым плечом — всех женщин рода.
Я женщина (мужчина) нашего рода.
Я одна (один) из вас.
Прямо сейчас я готова(готов) принять в дар ваше благословение.

Почувствуй ощущения в теле.
Какие возникают чувства?
Какие приходят образы?

Это может быть всё, что угодно.
Отпусти ум.
Не ищи логику.

Можно представить, как энергия наполняет тебя светом или цветом,
разливается теплом в теле.

Побудь в этом состоянии столько, сколько нужно.
Затем возвращайся в своём ритме.

Можно записать или зарисовать чувства, образы и состояния,
чтобы при желании к ним возвращаться.

После практики не обязательно сразу «закрывать» процесс.
Иногда состоянию нужно время, чтобы доработать внутри.
Дай этому быть."""


def reset_state(context):
    context.user_data["hellinger"] = {
        "mode": None,
        "theme": None,
    }


def get_state(context):
    return context.user_data.get("hellinger", {})


def kb_mode():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Практика «Род»", callback_data="h_mode_rod")],
        [InlineKeyboardButton("Расстановка", callback_data="h_mode_constellation")],
    ])


def kb_rod_start():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Начать практику", callback_data="h_rod_start")]
    ])


def kb_back_to_space():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Назад в пространство", callback_data="h_back_to_space")]
    ])


def kb_constellation_start():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Начать", callback_data="h_constellation_start")]
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
        [InlineKeyboardButton("Назад в пространство", callback_data="h_back_to_space")]
    ])


async def send_hellinger_entry(update, context):
    reset_state(context)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            "Ты можешь выбрать, как сейчас работать:\n\n"
            "— через пространство (расстановка с фигурами)\n"
            "— или через внутреннюю практику «Род»"
        ),
        reply_markup=kb_mode(),
    )


async def handle_hellinger_callback(update, context):
    query = update.callback_query
    if not query:
        return False

    data = query.data or ""

    if not data.startswith("h_"):
        return False

    try:
        await query.edit_message_reply_markup(None)
    except Exception:
        pass

    chat_id = update.effective_chat.id
    state = get_state(context)

    if data == "h_mode_rod":
        state["mode"] = "rod"
        await context.bot.send_message(
            chat_id=chat_id,
            text="Практика «Род»",
            reply_markup=kb_rod_start(),
        )
        return True

    if data == "h_rod_start":
        await context.bot.send_message(
            chat_id=chat_id,
            text=ROD_PRACTICE_TEXT,
            reply_markup=kb_back_to_space(),
        )
        return True

    if data == "h_mode_constellation":
        state["mode"] = "constellation"
        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                "Ты работаешь с пространством и фигурами.\n\n"
                "Это может быть что угодно:\n"
                "предметы, фигурки, вещи вокруг.\n\n"
                "Ты сам(а) создаёшь поле и смотришь, что в нём происходит.\n\n"
                "Бот не знает, что происходит в поле.\n"
                "Он не интерпретирует и не объясняет.\n\n"
                "Всё, что ты чувствуешь, видишь или понимаешь —\n"
                "это твоя информация из поля.\n\n"
                "Здесь нет правильных ответов.\n"
                "Есть только твой контакт с тем, что проявляется."
            ),
            reply_markup=kb_constellation_start(),
        )
        return True

    if data == "h_constellation_start":
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
                "— второй элемент\n\n"
                "Не спеши.\n"
                "Просто посмотри на них."
            ),
        )

        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                "Если хочется — можешь немного изменить их положение.\n\n"
                "Когда будешь готов(а) —\n"
                "дотронься до любой фигуры."
            ),
            reply_markup=kb_touch(),
        )
        return True

    if data == "h_touch":
        theme = state.get("theme")

        text = (
            "Дотронься до фигуры\n"
            "и посмотри, что появляется.\n\n"
            "Это может быть:\n"
            "— чувство\n"
            "— мысль\n"
            "— телесное ощущение\n"
            "— желание что-то изменить\n"
            "— или ничего\n\n"
            "Любая реакция — это информация.\n\n"
            "Фигура может:\n"
            "— двигаться\n"
            "— оставаться на месте\n"
            "— приближаться\n"
            "— отдаляться\n"
            "— «закрываться»\n\n"
            "Положение фигуры само по себе ничего не означает.\n"
            "Смысл знаешь только ты."
        )

        if theme == "h_theme_money":
            text += "\n\nМожно посмотреть:\n— как я отношусь к деньгам\n— могу ли подойти\n— могу ли взять"

        if theme == "h_theme_rel":
            text += "\n\nМожно посмотреть:\n— как я отношусь к партнёру\n— есть ли движение\n— что между вами"

        if theme == "h_theme_sit":
            text += "\n\nМожно посмотреть:\n— как я к этому отношусь\n— могу ли приблизиться\n— что происходит"

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
                "— двигать\n"
                "— приближать\n"
                "— отдалять\n"
                "— поворачивать"
            ),
        )

        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                "Если появляется напряжение или тяжесть —\n"
                "можно вынести это в отдельную фигуру.\n\n"
                "Ты можешь задать вопрос любой фигуре.\n"
                "Но ответ приходит не от бота,\n"
                "а через чувство, движение, образ\n"
                "или отсутствие реакции."
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
                "Когда почувствуешь, что достаточно —\n"
                "можешь завершить работу.\n\n"
                "Не обязательно сразу убирать поле.\n\n"
                "Иногда процесс продолжается\n"
                "и ему нужно время.\n\n"
                "Можно оставить всё как есть\n"
                "и дать этому доработать."
            ),
            reply_markup=kb_finish(),
        )
        return True

    if data == "h_back_to_space":
        from flows.paid_block.paid_space_flow import send_space_menu_text
        await send_space_menu_text(update, context)
        return True

    return False
