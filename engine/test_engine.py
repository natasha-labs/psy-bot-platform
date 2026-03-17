import asyncio
from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
)

from storage.results_store import save_user_result, get_user_results
from personality_code.aggregator import (
    enough_for_basic_personality_code,
    build_basic_personality_code,
)
from personality_code.renderer import (
    render_basic_personality_code,
    render_upsell_text,
    render_upsell_keyboard,
)

BACK_BUTTON = "⬅️ Назад"
RESTART_BUTTON = "🔄 Пройти тест заново"
TO_TESTS_BUTTON = "◀️ К выбору тестов"

TEST_SEQUENCE = ["archetype", "shadow", "anxiety"]


def get_nav_menu():
    keyboard = [
        [BACK_BUTTON],
        [RESTART_BUTTON],
        [TO_TESTS_BUTTON],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def build_progress_bar(current, total):
    blocks = 10
    filled = int((current / total) * blocks)
    empty = blocks - filled
    return "█" * filled + "░" * empty


def build_question_text(title, questions, index):
    total = len(questions)
    current = index + 1
    progress = build_progress_bar(current, total)

    return (
        "━━━━━━━━━━━━━━\n\n"
        f"Тест: {title}\n"
        f"Вопрос {current} / {total}\n\n"
        f"{questions[index]['text']}\n\n"
        "━━━━━━━━━━━━━━\n\n"
    )


def get_question_keyboard(question, selected=None):
    rows = []

    for i, option in enumerate(question["options"]):
        text = option["text"] if isinstance(option, dict) else option

        if selected == i:
            text = f"✔️ {text}"

        rows.append(
            [InlineKeyboardButton(text, callback_data=f"ans:{i}")]
        )

    return InlineKeyboardMarkup(rows)


def build_test_finished_text(total_questions):
    return (
        "━━━━━━━━━━━━━━\n\n"
        "Тест завершён\n\n"
        f"Вы ответили на {total_questions} вопросов.\n\n"
        "Система анализирует:\n"
        "• ваши реакции\n"
        "• эмоциональные паттерны\n"
        "• поведенческие стратегии\n\n"
        "━━━━━━━━━━━━━━"
    )


def get_finish_keyboard():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Показать результат", callback_data="show_result")],
            [InlineKeyboardButton("Пройти тест заново", callback_data="restart_test")],
        ]
    )


async def send_intro_screen(update, context, test_key, test_def):
    chat_id = update.effective_chat.id

    context.user_data["test"] = test_key
    context.user_data["stage"] = "intro"
    context.user_data["index"] = 0
    context.user_data["answers"] = []

    await context.bot.send_message(
        chat_id=chat_id,
        text=test_def["intro_text"],
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Начать тест", callback_data=f"start:{test_key}")],
                [InlineKeyboardButton("Назад", callback_data="main_menu")],
            ]
        ),
    )


async def send_question(update, context, test_def, index):
    chat_id = update.effective_chat.id
    question = test_def["questions"][index]

    text = build_question_text(test_def["title"], test_def["questions"], index)
    keyboard = get_question_keyboard(question)

    msg = await context.bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=keyboard,
    )

    context.user_data["message_id"] = msg.message_id


async def start_test(update, context, test_key, test_def):
    await send_intro_screen(update, context, test_key, test_def)


async def handle_callback(update, context, main_menu_markup, tests):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data.startswith("start:"):
        test_key = data.split(":")[1]
        test_def = tests[test_key]

        context.user_data["stage"] = "questions"
        context.user_data["index"] = 0
        context.user_data["answers"] = []

        await send_question(update, context, test_def, 0)
        return

    if data.startswith("ans:"):
        index = context.user_data["index"]
        test_key = context.user_data["test"]
        test_def = tests[test_key]

        option_index = int(data.split(":")[1])

        question = test_def["questions"][index]
        keyboard = get_question_keyboard(question, selected=option_index)

        text = build_question_text(test_def["title"], test_def["questions"], index)

        await query.edit_message_text(
            text=text,
            reply_markup=keyboard,
        )

        await asyncio.sleep(0.4)

        answer_value = test_def["get_option_value"](question["options"][option_index])
        context.user_data["answers"].append(answer_value)

        context.user_data["index"] += 1
        new_index = context.user_data["index"]

        if new_index >= len(test_def["questions"]):

            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=build_test_finished_text(len(test_def["questions"])),
                reply_markup=get_finish_keyboard(),
            )

            context.user_data["stage"] = "finished"
            return

        await send_question(update, context, test_def, new_index)
        return

    if data == "restart_test":
        test_key = context.user_data["test"]
        test_def = tests[test_key]

        context.user_data["index"] = 0
        context.user_data["answers"] = []

        await send_question(update, context, test_def, 0)
        return

    if data == "show_result":
        test_key = context.user_data["test"]
        test_def = tests[test_key]

        answers = context.user_data["answers"]

        result_payload = test_def["build_result"](answers)

        if isinstance(result_payload, dict):
            result_text = result_payload.get("text", "")
        else:
            result_text = result_payload

        user = update.effective_user

        if user:
            save_user_result(
                user.id,
                test_def["key"],
                test_def["title"],
                result_text,
            )

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=result_text,
        )

        context.user_data.clear()
