import asyncio
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


async def start_test(update, context, test_key, test_def):

    context.user_data["test"] = test_key
    context.user_data["answers"] = []
    context.user_data["q_index"] = 0

    await send_question(update, context, test_def)


async def send_question(update, context, test_def):

    q_index = context.user_data["q_index"]
    questions = test_def["questions"]

    question = questions[q_index]
    total = len(questions)

    text = (
        "━━━━━━━━━━━━━━\n\n"
        f"Тест: {test_def['title']}\n"
        f"Вопрос {q_index+1} / {total}\n\n"
        f"{question['text']}\n\n"
        "━━━━━━━━━━━━━━"
    )

    buttons = []

    for i, option in enumerate(question["options"]):

        buttons.append(
            [
                InlineKeyboardButton(
                    option,
                    callback_data=f"answer:{i}",
                )
            ]
        )

    keyboard = InlineKeyboardMarkup(buttons)

    if update.callback_query:
        await update.callback_query.message.edit_text(
            text,
            reply_markup=keyboard,
        )
    else:
        await update.message.reply_text(
            text,
            reply_markup=keyboard,
        )


async def handle_callback(update, context, main_menu_markup, TESTS):

    query = update.callback_query
    await query.answer()

    data = query.data

    if not data.startswith("answer:"):
        return

    test_key = context.user_data.get("test")

    if not test_key:
        return

    test_def = TESTS[test_key]

    q_index = context.user_data["q_index"]
    questions = test_def["questions"]
    question = questions[q_index]

    option_index = int(data.split(":")[1])
    option_text = question["options"][option_index]

    context.user_data["answers"].append(option_index)

    total = len(questions)

    text = (
        "━━━━━━━━━━━━━━\n\n"
        f"Тест: {test_def['title']}\n"
        f"Вопрос {q_index+1} / {total}\n\n"
        f"{question['text']}\n\n"
        "━━━━━━━━━━━━━━\n\n"
        f"✔️ Вы выбрали:\n{option_text}"
    )

    await query.message.edit_text(text)

    await asyncio.sleep(0.4)

    context.user_data["q_index"] += 1

    if context.user_data["q_index"] >= len(questions):

        await show_test_finished(update, context, test_def, main_menu_markup)

    else:

        await send_question(update, context, test_def)


async def show_test_finished(update, context, test_def, main_menu_markup):

    answers = context.user_data["answers"]

    text = (
        "━━━━━━━━━━━━━━\n\n"
        "Тест завершён\n\n"
        f"Вы ответили на {len(answers)} вопросов.\n\n"
        "Система анализирует:\n"
        "• ваши реакции\n"
        "• эмоциональные паттерны\n"
        "• поведенческие стратегии\n\n"
        "━━━━━━━━━━━━━━"
    )

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Показать результат",
                    callback_data="show_result",
                )
            ],
            [
                InlineKeyboardButton(
                    "Пройти тест заново",
                    callback_data="restart_test",
                )
            ],
        ]
    )

    await update.callback_query.message.edit_text(
        text,
        reply_markup=keyboard,
    )


async def show_result(update, context, test_def, main_menu_markup):

    answers = context.user_data["answers"]

    result_text = test_def["build_result"](answers)

    await update.callback_query.message.edit_text(
        result_text,
        reply_markup=main_menu_markup,
    )

    context.user_data.clear()
