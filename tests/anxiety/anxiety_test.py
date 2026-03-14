from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
)

from tests.anxiety.questions import questions as anxiety_questions


BACK_BUTTON = "⬅️ Назад"
RESTART_BUTTON = "🔄 Пройти тест заново"
TO_TESTS_BUTTON = "◀️ К выбору тестов"


def get_anxiety_nav_menu():
    keyboard = [
        [BACK_BUTTON],
        [RESTART_BUTTON],
        [TO_TESTS_BUTTON],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_intro_keyboard():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Поехали", callback_data="anxiety_start")],
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
        "🌫 *Уровень тревоги*\n\n"
        "Этот тест помогает понять, сколько внутреннего напряжения и тревоги "
        "сейчас присутствует в вашем фоне.\n\n"
        "*Как отвечать:*\n"
        "Читайте вопрос и выбирайте вариант, который ближе всего вашему обычному состоянию.\n\n"
        "Здесь нет правильных или неправильных ответов.\n"
        "Важно отвечать честно, не занижая и не приукрашивая ощущения.\n\n"
        "Нажмите *Поехали*, чтобы начать тест."
    )


def build_question_text(index):
    question = anxiety_questions[index]
    return (
        f"Тест: Уровень тревоги\n\n"
        f"Вопрос {index + 1} из {len(anxiety_questions)}:\n"
        f"{question['text']}"
    )


def build_anxiety_result(answers):
    score = 0

    for a in answers:
        if a in ["почти никогда", "спокойно реагируешь", "чувствуешь спокойную концентрацию"]:
            score += 1
        elif a in ["иногда", "немного напрягаешься", "немного волнуешься"]:
            score += 2
        elif a in ["часто", "сильно переживаешь", "долго прокручиваешь мысли"]:
            score += 3
        else:
            score += 4

    if score <= 25:
        return (
            "🟢 *УРОВЕНЬ ТРЕВОГИ: НИЗКИЙ*\n\n"
            "Сейчас тревога, скорее всего, не доминирует в фоне жизни.\n"
            "Есть достаточный уровень внутренней устойчивости и опоры."
        )

    if score <= 50:
        return (
            "🟡 *УРОВЕНЬ ТРЕВОГИ: УМЕРЕННЫЙ*\n\n"
            "Тревога присутствует, но не захватывает вас полностью.\n"
            "Иногда она влияет на мысли, решения и внутреннее напряжение."
        )

    return (
        "🔴 *УРОВЕНЬ ТРЕВОГИ: ПОВЫШЕННЫЙ*\n\n"
        "Похоже, тревога сейчас заметно влияет на внутреннее состояние.\n"
        "Может быть много фонового напряжения, прокручивания мыслей и ожидания сложностей."
    )


async def send_anxiety_question(update, context, index):
    question = anxiety_questions[index]

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=build_question_text(index),
        reply_markup=get_question_keyboard(question),
    )


async def start_anxiety_test(update, context):
    context.user_data["test"] = "anxiety"
    context.user_data["anxiety_stage"] = "intro"
    context.user_data["index"] = 0
    context.user_data["answers"] = []

    await update.message.reply_text(
        build_intro_text(),
        reply_markup=get_intro_keyboard(),
        parse_mode="Markdown",
    )


async def handle_anxiety_nav(action, update, context, main_menu_markup):
    current_test = context.user_data.get("test")
    if current_test != "anxiety":
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

    if action == "anxiety_start":
        context.user_data["anxiety_stage"] = "questions"
        context.user_data["index"] = 0
        context.user_data["answers"] = []

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Тест начат.",
            reply_markup=get_anxiety_nav_menu(),
        )
        await send_anxiety_question(update, context, 0)
        return

    if context.user_data.get("anxiety_stage") != "questions":
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
        await send_anxiety_question(update, context, 0)
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
        await send_anxiety_question(update, context, context.user_data["index"])
        return

    if action.startswith("ans_"):
        index = context.user_data.get("index", 0)
        current_question = anxiety_questions[index]

        option_index = int(action.split("_")[1])

        if option_index < 0 or option_index >= len(current_question["options"]):
            await update.callback_query.answer("Такого варианта нет", show_alert=False)
            return

        selected_option = current_question["options"][option_index]
        context.user_data["answers"].append(selected_option)
        context.user_data["index"] = index + 1

        new_index = context.user_data["index"]

        if new_index >= len(anxiety_questions):
            result_text = build_anxiety_result(context.user_data["answers"])
            context.user_data.clear()

            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=result_text,
                parse_mode="Markdown",
                reply_markup=main_menu_markup,
            )
            return

        await send_anxiety_question(update, context, new_index)
        return


async def handle_anxiety_answer(update, context, main_menu_markup):
    text = update.message.text
    stage = context.user_data.get("anxiety_stage")

    if text == BACK_BUTTON:
        if stage == "intro":
            context.user_data.clear()
            await update.message.reply_text(
                "Выберите тест:",
                reply_markup=main_menu_markup,
            )
            return
        await handle_anxiety_nav("back", update, context, main_menu_markup)
        return

    if text == RESTART_BUTTON:
        if stage == "intro":
            await update.message.reply_text(
                "Сначала нажмите «Поехали».",
            )
            return
        await handle_anxiety_nav("restart", update, context, main_menu_markup)
        return

    if text == TO_TESTS_BUTTON:
        await handle_anxiety_nav("to_tests", update, context, main_menu_markup)
        return

    await update.message.reply_text(
        "Для ответа используйте кнопки в сообщении с вопросом.",
        reply_markup=get_anxiety_nav_menu() if stage == "questions" else main_menu_markup,
    )