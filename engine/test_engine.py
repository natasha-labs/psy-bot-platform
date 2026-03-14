from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
)

from storage.results_store import save_user_result

BACK_BUTTON = "⬅️ Назад"
RESTART_BUTTON = "🔄 Пройти тест заново"
TO_TESTS_BUTTON = "◀️ К выбору тестов"


def get_nav_menu():
    keyboard = [
        [BACK_BUTTON],
        [RESTART_BUTTON],
        [TO_TESTS_BUTTON],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_intro_keyboard(test_key: str):
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Поехали", callback_data=f"start:{test_key}")],
            [InlineKeyboardButton("Назад", callback_data="main_menu")],
        ]
    )


def get_choice_emoji(index: int) -> str:
    emojis = ["①", "②", "③", "④", "⑤", "⑥"]
    return emojis[index] if index < len(emojis) else f"{index + 1}."


def build_option_cards(question, get_option_text):
    lines = []
    for option_index, option in enumerate(question["options"]):
        emoji = get_choice_emoji(option_index)
        text = get_option_text(option)
        lines.append(f"{emoji} {text}")
    return "\n\n".join(lines)


def get_question_keyboard(question):
    rows = []

    for option_index, option in enumerate(question["options"]):
        text = option["text"] if isinstance(option, dict) else option
        rows.append(
            [
                InlineKeyboardButton(
                    text,
                    callback_data=f"ans:{option_index}"
                )
            ]
        )

    return InlineKeyboardMarkup(rows)


def build_question_text(title: str, questions, index: int, get_option_text) -> str:
    question = questions[index]

    return (
        f"Тест: {title}\n\n"
        f"Вопрос {index + 1} из {len(questions)}:\n"
        f"{question['text']}"
    )


async def send_question(update, context, test_def, index: int):
    question = test_def["questions"][index]

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=build_question_text(
            test_def["title"],
            test_def["questions"],
            index,
            test_def["get_option_text"],
        ),
        reply_markup=get_question_keyboard(question),
    )


async def start_test(update, context, test_key: str, test_def):
    context.user_data["test"] = test_key
    context.user_data["stage"] = "intro"
    context.user_data["index"] = 0
    context.user_data["answers"] = []

    await update.message.reply_text(
        test_def["intro_text"],
        reply_markup=get_intro_keyboard(test_key),
        parse_mode="Markdown",
    )


async def begin_test(update, context, test_key: str, test_def):
    context.user_data["test"] = test_key
    context.user_data["stage"] = "questions"
    context.user_data["index"] = 0
    context.user_data["answers"] = []

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Тест начат.",
        reply_markup=get_nav_menu(),
    )
    await send_question(update, context, test_def, 0)


async def handle_nav_text(update, context, main_menu_markup, tests):
    text = update.message.text
    current_test = context.user_data.get("test")
    stage = context.user_data.get("stage")

    if not current_test or current_test not in tests:
        await update.message.reply_text(
            "Выберите тест:",
            reply_markup=main_menu_markup,
        )
        return

    test_def = tests[current_test]

    if text == BACK_BUTTON:
        if stage == "intro":
            context.user_data.clear()
            await update.message.reply_text(
                "Выберите тест:",
                reply_markup=main_menu_markup,
            )
            return

        index = context.user_data.get("index", 0)
        answers = context.user_data.get("answers", [])

        if index == 0:
            await update.message.reply_text(
                "Это первый вопрос теста.",
                reply_markup=get_nav_menu(),
            )
            return

        context.user_data["index"] = index - 1
        if answers:
            answers.pop()

        await update.message.reply_text(
            "Возвращаемся на предыдущий вопрос.",
            reply_markup=get_nav_menu(),
        )
        await send_question(update, context, test_def, context.user_data["index"])
        return

    if text == RESTART_BUTTON:
        if stage != "questions":
            await update.message.reply_text(
                "Сначала нажмите «Поехали».",
                reply_markup=main_menu_markup,
            )
            return

        context.user_data["index"] = 0
        context.user_data["answers"] = []

        await update.message.reply_text(
            "Тест начат заново.",
            reply_markup=get_nav_menu(),
        )
        await send_question(update, context, test_def, 0)
        return

    if text == TO_TESTS_BUTTON:
        context.user_data.clear()
        await update.message.reply_text(
            "Выберите тест:",
            reply_markup=main_menu_markup,
        )
        return

    await update.message.reply_text(
        "Для ответа используйте кнопки под вопросом.",
        reply_markup=get_nav_menu() if stage == "questions" else main_menu_markup,
    )


async def handle_callback(update, context, main_menu_markup, tests):
    query = update.callback_query
    await query.answer()

    data = query.data
    current_test = context.user_data.get("test")

    if data == "main_menu":
        context.user_data.clear()
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Выберите тест:",
            reply_markup=main_menu_markup,
        )
        return

    if data.startswith("start:"):
        test_key = data.split(":", 1)[1]
        if test_key not in tests:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Этот тест сейчас недоступен.",
                reply_markup=main_menu_markup,
            )
            return

        await begin_test(update, context, test_key, tests[test_key])
        return

    if not current_test or current_test not in tests:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Выберите тест:",
            reply_markup=main_menu_markup,
        )
        return

    if not data.startswith("ans:"):
        return

    test_def = tests[current_test]
    index = context.user_data.get("index", 0)
    current_question = test_def["questions"][index]

    option_index = int(data.split(":")[1])

    if option_index < 0 or option_index >= len(current_question["options"]):
        await query.answer("Такого варианта нет", show_alert=False)
        return

    selected_option = current_question["options"][option_index]
    answer_value = test_def["get_option_value"](selected_option)

    context.user_data["answers"].append(answer_value)
    context.user_data["index"] = index + 1

    new_index = context.user_data["index"]

    if new_index >= len(test_def["questions"]):
        result_text = test_def["build_result"](context.user_data["answers"])

        user = update.effective_user
        if user:
            save_user_result(
                user_id=user.id,
                test_key=test_def["key"],
                title=test_def["title"],
                result_text=result_text,
            )

        context.user_data.clear()

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=result_text,
            parse_mode="Markdown",
            reply_markup=main_menu_markup,
        )
        return

    await send_question(update, context, test_def, new_index)
