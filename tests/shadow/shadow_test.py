from collections import Counter
from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
)

from tests.shadow.questions import questions as shadow_questions


CATEGORY_LABELS = {
    "control": "Контроль",
    "weakness": "Уязвимость",
    "anger": "Агрессия",
    "fear": "Страх",
}

SHADOW_TYPES = {
    "control": "Контролёр",
    "weakness": "Ранимый",
    "anger": "Бунтарь",
    "fear": "Тревожный",
}

BACK_BUTTON = "⬅️ Назад"
RESTART_BUTTON = "🔄 Пройти тест заново"
TO_TESTS_BUTTON = "◀️ К выбору тестов"


def get_shadow_nav_menu():
    keyboard = [
        [BACK_BUTTON],
        [RESTART_BUTTON],
        [TO_TESTS_BUTTON],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_question_keyboard(question):
    rows = []
    for option_index, option in enumerate(question["options"]):
        rows.append(
            [InlineKeyboardButton(option["text"], callback_data=f"ans_{option_index}")]
        )
    return InlineKeyboardMarkup(rows)


def get_intro_keyboard():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Поехали", callback_data="shadow_start")],
            [InlineKeyboardButton("Назад", callback_data="main_menu")],
        ]
    )


def build_intro_text():
    return (
        "🌑 *Код Тени*\n\n"
        "Этот тест помогает увидеть скрытые психологические паттерны и реакции, "
        "которые обычно остаются вне внимания.\n\n"
        "*Как отвечать:*\n"
        "Читайте вопрос и выбирайте вариант ответа, который ближе всего вам.\n\n"
        "Здесь нет правильных или неправильных ответов.\n"
        "Важно отвечать честно и не пытаться выбирать «хорошие» варианты.\n\n"
        "Иногда первый импульс — самый точный.\n\n"
        "Нажмите *Поехали*, чтобы начать тест."
    )


def build_question_text(index):
    question = shadow_questions[index]
    return (
        f"Тест: Код Тени\n\n"
        f"Вопрос {index + 1} из {len(shadow_questions)}:\n"
        f"{question['text']}"
    )


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
    if main_type == "control":
        return (
            "Этот тип Тени формируется там, где человеку важно держать себя, чувства и ситуацию под контролем.\n"
            "Снаружи это может выглядеть как собранность и сила, а внутри часто скрывается напряжение и запрет на слабость."
        )

    if main_type == "weakness":
        return (
            "Этот тип Тени связан с глубокой чувствительностью, которую человек привыкает прятать.\n"
            "Снаружи это может быть спокойствие или отстранённость, а внутри — ранимость и страх быть слишком открытым."
        )

    if main_type == "anger":
        return (
            "Этот тип Тени связан с подавленной злостью, силой и резкостью.\n"
            "Человек может долго сдерживаться, но внутри копится энергия, которая ищет выход."
        )

    return (
        "Этот тип Тени связан с тревогой, внутренней настороженностью и ожиданием напряжения.\n"
        "Снаружи человек может казаться собранным, но внутри часто живёт страх ошибки, угрозы или потери опоры."
    )


def build_main_interpretation(main_type):
    if main_type == "control":
        return (
            "🔎 *ГЛАВНАЯ ТЕМА ТЕНИ*\n"
            "Контроль и защита\n\n"
            "Похоже, твоя психика чаще всего выбирает контроль как способ справляться с напряжением.\n\n"
            "Что это может значить:\n"
            "• тебе трудно расслабляться, когда ситуация не под контролем\n"
            "• ты можешь собираться и держаться очень сильно, даже когда внутри тяжело\n"
            "• уязвимость чаще прячется за собранностью, жёсткостью или внутренней дисциплиной\n\n"
            "Точка роста:\n"
            "разрешить себе не только держать ситуацию, но и замечать живые чувства под этим контролем."
        )

    if main_type == "weakness":
        return (
            "🔎 *ГЛАВНАЯ ТЕМА ТЕНИ*\n"
            "Подавленная уязвимость\n\n"
            "Похоже, главная теневая тема сейчас связана с ранимостью, слабостью и желанием закрыться.\n\n"
            "Что это может значить:\n"
            "• тебе может быть трудно показывать, что тебе больно, страшно или не хватает опоры\n"
            "• внутри может жить запрет на слабость\n"
            "• в напряжённых ситуациях есть тенденция уходить внутрь, а не проявляться наружу\n\n"
            "Точка роста:\n"
            "учиться видеть в уязвимости не слабость, а живую часть себя."
        )

    if main_type == "anger":
        return (
            "🔎 *ГЛАВНАЯ ТЕМА ТЕНИ*\n"
            "Подавленная агрессия\n\n"
            "Похоже, в твоей Тени сильнее всего звучит тема злости, силы и резкой реакции.\n\n"
            "Что это может значить:\n"
            "• тебя особенно задевают агрессивные проявления других людей\n"
            "• собственная злость может подавляться или считаться неправильной\n"
            "• иногда напряжение прорывается в раздражении, резких мыслях или ответах\n\n"
            "Точка роста:\n"
            "учиться признавать злость как энергию границ, а не только как угрозу."
        )

    return (
        "🔎 *ГЛАВНАЯ ТЕМА ТЕНИ*\n"
        "Подавленный страх\n\n"
        "Похоже, сейчас в твоей Тени сильнее всего звучит тема страха, тревоги и внутренней настороженности.\n\n"
        "Что это может значить:\n"
        "• внутри может быть много напряжения, даже если снаружи это не видно\n"
        "• часть реакций рождается из ожидания угрозы\n"
        "• тебе может быть сложно до конца расслабиться и доверять происходящему\n\n"
        "Точка роста:\n"
        "не бороться со страхом, а распознавать его как важный внутренний сигнал."
    )


def build_second_interpretation(second_type):
    if second_type == "control":
        return "Второй слой Тени связан с контролем: тебе важно удерживать внутреннюю и внешнюю стабильность."
    if second_type == "weakness":
        return "Второй слой Тени связан с уязвимостью: внутри есть чувствительная часть, которую не всегда легко показывать."
    if second_type == "anger":
        return "Второй слой Тени связан с агрессией: часть силы и злости может быть сдержана или вытеснена."
    return "Второй слой Тени связан со страхом: внутри может быть много настороженности и ожидания напряжения."


def build_shadow_result(answer_values):
    percentages, main_type, second_type = calculate_profile(answer_values)

    type_name = SHADOW_TYPES[main_type]
    type_description = build_type_description(main_type)
    main_text = build_main_interpretation(main_type)
    second_text = build_second_interpretation(second_type)

    profile_block = (
        f"Контроль — {percentages['control']}%\n"
        f"Агрессия — {percentages['anger']}%\n"
        f"Уязвимость — {percentages['weakness']}%\n"
        f"Страх — {percentages['fear']}%"
    )

    return (
        f"🌑 *ТВОЙ ТИП ТЕНИ*\n"
        f"{type_name}\n\n"
        f"{type_description}\n\n"
        f"━━━━━━━━━━━━━━\n\n"
        f"{main_text}\n\n"
        f"━━━━━━━━━━━━━━\n\n"
        f"📊 *ПРОФИЛЬ ТЕНИ*\n"
        f"{profile_block}\n\n"
        f"━━━━━━━━━━━━━━\n\n"
        f"🌘 *ВТОРОЙ СЛОЙ ТЕНИ*\n"
        f"{CATEGORY_LABELS[second_type]}\n"
        f"{second_text}"
    )


async def send_shadow_question(update, context, index):
    question = shadow_questions[index]

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=build_question_text(index),
        reply_markup=get_question_keyboard(question),
    )


async def start_shadow_test(update, context):
    context.user_data["test"] = "shadow"
    context.user_data["shadow_stage"] = "intro"
    context.user_data["index"] = 0
    context.user_data["answers"] = []

    await update.message.reply_text(
        build_intro_text(),
        reply_markup=get_intro_keyboard(),
        parse_mode="Markdown",
    )


async def handle_shadow_nav(action, update, context, main_menu_markup):
    current_test = context.user_data.get("test")
    if current_test != "shadow":
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

    if action == "shadow_start":
        context.user_data["shadow_stage"] = "questions"
        context.user_data["index"] = 0
        context.user_data["answers"] = []

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Тест начат.",
            reply_markup=get_shadow_nav_menu(),
        )
        await send_shadow_question(update, context, 0)
        return

    if context.user_data.get("shadow_stage") != "questions":
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
        await send_shadow_question(update, context, 0)
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
        await send_shadow_question(update, context, context.user_data["index"])
        return

    if action.startswith("ans_"):
        index = context.user_data.get("index", 0)
        current_question = shadow_questions[index]

        option_index = int(action.split("_")[1])

        if option_index < 0 or option_index >= len(current_question["options"]):
            await update.callback_query.answer("Такого варианта нет", show_alert=False)
            return

        selected_option = current_question["options"][option_index]
        context.user_data["answers"].append(selected_option["value"])
        context.user_data["index"] = index + 1

        new_index = context.user_data["index"]

        if new_index >= len(shadow_questions):
            result_text = build_shadow_result(context.user_data["answers"])
            context.user_data.clear()

            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=result_text,
                parse_mode="Markdown",
                reply_markup=main_menu_markup,
            )
            return

        await send_shadow_question(update, context, new_index)
        return


async def handle_shadow_answer(update, context, main_menu_markup):
    text = update.message.text
    stage = context.user_data.get("shadow_stage")

    if text == BACK_BUTTON:
        if stage == "intro":
            context.user_data.clear()
            await update.message.reply_text(
                "Выберите тест:",
                reply_markup=main_menu_markup,
            )
            return
        await handle_shadow_nav("back", update, context, main_menu_markup)
        return

    if text == RESTART_BUTTON:
        if stage == "intro":
            await update.message.reply_text(
                "Сначала нажмите «Поехали».",
            )
            return
        await handle_shadow_nav("restart", update, context, main_menu_markup)
        return

    if text == TO_TESTS_BUTTON:
        await handle_shadow_nav("to_tests", update, context, main_menu_markup)
        return

    await update.message.reply_text(
        "Для ответа используйте кнопки в сообщении с вопросом.",
        reply_markup=get_shadow_nav_menu() if stage == "questions" else main_menu_markup,
    )