from collections import Counter
from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
)

from tests.archetype.questions import questions as archetype_questions


CATEGORY_LABELS = {
    "leader": "Лидерство",
    "observer": "Наблюдение",
    "supporter": "Поддержка",
    "free": "Свобода",
}

ARCHETYPE_TYPES = {
    "leader": "Лидер",
    "observer": "Наблюдатель",
    "supporter": "Поддерживающий",
    "free": "Свободный",
}

BACK_BUTTON = "⬅️ Назад"
RESTART_BUTTON = "🔄 Пройти тест заново"
TO_TESTS_BUTTON = "◀️ К выбору тестов"


def get_archetype_nav_menu():
    keyboard = [
        [BACK_BUTTON],
        [RESTART_BUTTON],
        [TO_TESTS_BUTTON],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_intro_keyboard():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Поехали", callback_data="archetype_start")],
            [InlineKeyboardButton("Назад", callback_data="main_menu")],
        ]
    )


def get_question_keyboard(question):
    rows = []
    for option_index, option in enumerate(question["options"]):
        rows.append(
            [InlineKeyboardButton(option, callback_data=f"ans_{option_index}")]
        )
    return InlineKeyboardMarkup(rows)


def build_intro_text():
    return (
        "✨ *Архетип личности*\n\n"
        "Этот тест помогает увидеть ваш ведущий стиль поведения, способ взаимодействия с миром "
        "и внутреннюю роль, через которую вы чаще всего проявляетесь.\n\n"
        "*Как отвечать:*\n"
        "Читайте вопрос и выбирайте тот вариант, который ближе всего вам.\n\n"
        "Здесь нет правильных или неправильных ответов.\n"
        "Важно отвечать не «как лучше», а как для вас естественно.\n\n"
        "Нажмите *Поехали*, чтобы начать тест."
    )


def build_question_text(index):
    question = archetype_questions[index]
    return (
        f"Тест: Архетип личности\n\n"
        f"Вопрос {index + 1} из {len(archetype_questions)}:\n"
        f"{question['text']}"
    )


def map_answer_to_value(answer_text):
    mapping = {
        "берёшь инициативу на себя": "leader",
        "действуешь быстро": "leader",
        "берёшь руководство ситуацией": "leader",
        "влиять на решения": "leader",
        "решаешь быстро": "leader",
        "предлагаешь решение": "leader",
        "вести процесс": "leader",
        "берёшь контроль": "leader",
        "хочешь реализовать её": "leader",
        "пытаешься направить разговор": "leader",

        "наблюдаешь и присматриваешься": "observer",
        "анализируешь": "observer",
        "наблюдаешь и оцениваешь": "observer",
        "понимать процессы": "observer",
        "сначала собираешь информацию": "observer",
        "слушаешь и наблюдаешь": "observer",
        "разобраться в деталях": "observer",
        "наблюдаешь": "observer",
        "хочешь понять её глубже": "observer",
        "слушаешь и анализируешь": "observer",

        "стараешься поддержать атмосферу": "supporter",
        "ищешь, кого поддержать": "supporter",
        "пытаешься примирить": "supporter",
        "помогать людям": "supporter",
        "советуешься с людьми": "supporter",
        "поддерживаешь эмоционально": "supporter",
        "работать с людьми": "supporter",
        "держишь контакт с людьми": "supporter",
        "хочешь обсудить её": "supporter",
        "сглаживаешь конфликт": "supporter",

        "держишь дистанцию": "free",
        "сохраняешь свободу действий": "free",
        "отстраняешься": "free",
        "работать самостоятельно": "free",
        "оставляешь себе пространство выбора": "free",
        "даёшь пространство": "free",
        "делать по-своему": "free",
        "сохраняешь независимость": "free",
        "оставляешь её себе": "free",
        "отходишь в сторону": "free",
    }
    return mapping[answer_text]


def calculate_profile(answer_values):
    counts = Counter(answer_values)

    for key in CATEGORY_LABELS:
        if key not in counts:
            counts[key] = 0

    total = sum(counts.values())

    percentages = {}
    for key in CATEGORY_LABELS:
        percentages[key] = 0 if total == 0 else round(counts[key] / total * 100)

    sorted_profiles = sorted(
        percentages.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    main_type = sorted_profiles[0][0]
    second_type = sorted_profiles[1][0]

    return percentages, main_type, second_type


def build_type_description(main_type):
    if main_type == "leader":
        return (
            "Этот тип личности тянется к влиянию, движению и внутренней опоре.\n"
            "Такой человек часто чувствует потребность направлять процесс, принимать решения и брать ответственность."
        )

    if main_type == "observer":
        return (
            "Этот тип личности сначала смотрит, чувствует контекст и только потом действует.\n"
            "Ему важно понять глубину происходящего и увидеть скрытый смысл ситуации."
        )

    if main_type == "supporter":
        return (
            "Этот тип личности ориентирован на контакт, тепло и поддержку.\n"
            "Такой человек тонко чувствует других и часто становится эмоциональной опорой для окружающих."
        )

    return (
        "Этот тип личности особенно ценит пространство, независимость и внутреннюю честность.\n"
        "Ему важно сохранять право быть собой и не растворяться в чужих ожиданиях."
    )


def build_main_interpretation(main_type):
    if main_type == "leader":
        return (
            "🔎 *ВЕДУЩАЯ ТЕМА АРХЕТИПА*\n"
            "Лидерство и влияние\n\n"
            "Похоже, вы естественно тянетесь к позиции, где можно влиять, вести и задавать направление.\n\n"
            "Что это может значить:\n"
            "• вам легче включаться, когда есть цель и движение\n"
            "• внутри есть сильная опора на решение и действие\n"
            "• вам может быть трудно долго находиться в пассивной роли\n\n"
            "Точка роста:\n"
            "не только вести, но и иногда разрешать себе не знать ответ сразу."
        )

    if main_type == "observer":
        return (
            "🔎 *ВЕДУЩАЯ ТЕМА АРХЕТИПА*\n"
            "Наблюдение и глубина\n\n"
            "Похоже, вы лучше всего раскрываетесь через наблюдение, понимание и внутренний анализ.\n\n"
            "Что это может значить:\n"
            "• вам важно сначала почувствовать контекст\n"
            "• вы замечаете детали, которые другие могут пропустить\n"
            "• перед действием вам нужно внутреннее понимание\n\n"
            "Точка роста:\n"
            "не застревать в наблюдении и иногда идти в действие чуть раньше."
        )

    if main_type == "supporter":
        return (
            "🔎 *ВЕДУЩАЯ ТЕМА АРХЕТИПА*\n"
            "Поддержка и контакт\n\n"
            "Похоже, ваша сильная сторона — создавать тепло, удерживать связь и поддерживать людей рядом.\n\n"
            "Что это может значить:\n"
            "• вы тонко чувствуете эмоциональную атмосферу\n"
            "• рядом с вами людям легче раскрываться\n"
            "• вам естественно быть опорой и заботой\n\n"
            "Точка роста:\n"
            "не забывать о себе, пока поддерживаете других."
        )

    return (
        "🔎 *ВЕДУЩАЯ ТЕМА АРХЕТИПА*\n"
        "Свобода и дистанция\n\n"
        "Похоже, для вас особенно важны внутреннее пространство, самостоятельность и право быть собой.\n\n"
        "Что это может значить:\n"
        "• вам трудно находиться в слишком тесных рамках\n"
        "• важна независимость решений и ощущение свободы\n"
        "• иногда дистанция становится способом сохранить себя\n\n"
        "Точка роста:\n"
        "не путать свободу с изоляцией и оставлять место для близости."
    )


def build_second_interpretation(second_type):
    if second_type == "leader":
        return "Второй слой архетипа связан с лидерством: внутри есть стремление влиять, вести и принимать решения."
    if second_type == "observer":
        return "Второй слой архетипа связан с наблюдением: внутри есть сильная аналитическая и чувствующая часть."
    if second_type == "supporter":
        return "Второй слой архетипа связан с поддержкой: внутри есть тепло, эмпатия и готовность быть опорой."
    return "Второй слой архетипа связан со свободой: внутри есть сильная потребность в независимости и собственном пространстве."


def build_archetype_result(answer_values):
    percentages, main_type, second_type = calculate_profile(answer_values)

    type_name = ARCHETYPE_TYPES[main_type]
    type_description = build_type_description(main_type)
    main_text = build_main_interpretation(main_type)
    second_text = build_second_interpretation(second_type)

    profile_block = (
        f"Лидерство — {percentages['leader']}%\n"
        f"Наблюдение — {percentages['observer']}%\n"
        f"Поддержка — {percentages['supporter']}%\n"
        f"Свобода — {percentages['free']}%"
    )

    return (
        f"✨ *ТВОЙ ТИП АРХЕТИПА*\n"
        f"{type_name}\n\n"
        f"{type_description}\n\n"
        f"━━━━━━━━━━━━━━\n\n"
        f"{main_text}\n\n"
        f"━━━━━━━━━━━━━━\n\n"
        f"📊 *ПРОФИЛЬ АРХЕТИПА*\n"
        f"{profile_block}\n\n"
        f"━━━━━━━━━━━━━━\n\n"
        f"🌗 *ВТОРОЙ СЛОЙ АРХЕТИПА*\n"
        f"{CATEGORY_LABELS[second_type]}\n"
        f"{second_text}"
    )


async def send_archetype_question(update, context, index):
    question = archetype_questions[index]

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=build_question_text(index),
        reply_markup=get_question_keyboard(question),
    )


async def start_archetype_test(update, context):
    context.user_data["test"] = "archetype"
    context.user_data["archetype_stage"] = "intro"
    context.user_data["index"] = 0
    context.user_data["answers"] = []

    await update.message.reply_text(
        build_intro_text(),
        reply_markup=get_intro_keyboard(),
        parse_mode="Markdown",
    )


async def handle_archetype_nav(action, update, context, main_menu_markup):
    current_test = context.user_data.get("test")
    if current_test != "archetype":
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Выберите тест:",
            reply_markup=main_menu_markup,
        )
        return

    if action == "main_menu":
        context.user_data.clear()
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Выберите тест:",
            reply_markup=main_menu_markup,
        )
        return

    if action == "archetype_start":
        context.user_data["archetype_stage"] = "questions"
        context.user_data["index"] = 0
        context.user_data["answers"] = []

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Тест начат.",
            reply_markup=get_archetype_nav_menu(),
        )
        await send_archetype_question(update, context, 0)
        return

    if context.user_data.get("archetype_stage") != "questions":
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Нажмите «Поехали», чтобы начать тест.",
        )
        return

    if action == "restart":
        context.user_data["index"] = 0
        context.user_data["answers"] = []
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Тест начат заново.",
        )
        await send_archetype_question(update, context, 0)
        return

    if action == "to_tests":
        context.user_data.clear()
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Выберите тест:",
            reply_markup=main_menu_markup,
        )
        return

    if action == "back":
        index = context.user_data.get("index", 0)
        answers = context.user_data.get("answers", [])

        if index == 0:
            await update.callback_query.answer("Это первый вопрос", show_alert=False)
            return

        context.user_data["index"] = index - 1
        if answers:
            answers.pop()

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Возвращаемся на предыдущий вопрос.",
        )
        await send_archetype_question(update, context, context.user_data["index"])
        return

    if action.startswith("ans_"):
        index = context.user_data.get("index", 0)
        current_question = archetype_questions[index]

        option_index = int(action.split("_")[1])

        if option_index < 0 or option_index >= len(current_question["options"]):
            await update.callback_query.answer("Такого варианта нет", show_alert=False)
            return

        selected_option = current_question["options"][option_index]
        context.user_data["answers"].append(map_answer_to_value(selected_option))
        context.user_data["index"] = index + 1

        new_index = context.user_data["index"]

        if new_index >= len(archetype_questions):
            result_text = build_archetype_result(context.user_data["answers"])
            context.user_data.clear()

            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=result_text,
                parse_mode="Markdown",
                reply_markup=main_menu_markup,
            )
            return

        await send_archetype_question(update, context, new_index)
        return


async def handle_archetype_answer(update, context, main_menu_markup):
    text = update.message.text
    stage = context.user_data.get("archetype_stage")

    if text == BACK_BUTTON:
        if stage == "intro":
            context.user_data.clear()
            await update.message.reply_text(
                "Выберите тест:",
                reply_markup=main_menu_markup,
            )
            return
        await handle_archetype_nav("back", update, context, main_menu_markup)
        return

    if text == RESTART_BUTTON:
        if stage == "intro":
            await update.message.reply_text(
                "Сначала нажмите «Поехали».",
            )
            return
        await handle_archetype_nav("restart", update, context, main_menu_markup)
        return

    if text == TO_TESTS_BUTTON:
        await handle_archetype_nav("to_tests", update, context, main_menu_markup)
        return

    await update.message.reply_text(
        "Для ответа используйте кнопки в сообщении с вопросом.",
        reply_markup=get_archetype_nav_menu() if stage == "questions" else main_menu_markup,
    )