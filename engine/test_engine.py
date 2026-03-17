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
    render_basic_code_ready_text,
    render_basic_code_ready_keyboard,
)

BACK_BUTTON = "⬅️ Назад"
RESTART_BUTTON = "🔄 Пройти тест заново"
TO_TESTS_BUTTON = "◀️ К выбору тестов"

TEST_SEQUENCE = ["archetype", "shadow", "anxiety"]

TEST_BUTTON_LABELS = {
    "archetype": "Архетип личности",
    "shadow": "Код Тени",
    "anxiety": "Внутреннее напряжение",
}


def get_nav_menu():
    keyboard = [
        [BACK_BUTTON],
        [RESTART_BUTTON],
        [TO_TESTS_BUTTON],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def has_full_access(results: dict) -> bool:
    required = {"archetype", "shadow", "anxiety"}
    return required.issubset(set(results.keys()))


def get_dynamic_main_menu(user_id):
    results = get_user_results(user_id)

    if has_full_access(results):
        keyboard = [
            ["Архетип личности"],
            ["Код Тени"],
            ["Внутреннее напряжение"],
            ["Мои результаты"],
            ["Получить Код личности"],
            ["О тесте"],
        ]
    else:
        keyboard = [
            ["Начать исследование"],
            ["Мои результаты"],
            ["О тесте"],
        ]

    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_intro_keyboard(test_key: str):
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Начать тест", callback_data=f"start:{test_key}")],
            [InlineKeyboardButton("Назад", callback_data="main_menu")],
        ]
    )


def build_question_text(title: str, questions, index: int) -> str:
    question = questions[index]
    total = len(questions)
    current = index + 1

    return (
        "━━━━━━━━━━━━━━\n\n"
        f"Тест: {title}\n"
        f"Вопрос {current} / {total}\n\n"
        f"{question['text']}\n\n"
        "━━━━━━━━━━━━━━"
    )


def get_question_keyboard(question, selected_index=None):
    rows = []

    for option_index, option in enumerate(question["options"]):
        text = option["text"]

        if selected_index is not None and selected_index == option_index:
            text = f"✔️ ВЫБРАНО: {text}"

        rows.append(
            [
                InlineKeyboardButton(
                    text,
                    callback_data=f"ans:{option_index}",
                )
            ]
        )

    return InlineKeyboardMarkup(rows)


def get_share_keyboard(share_text):
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Поделиться результатом",
                    switch_inline_query=share_text,
                )
            ]
        ]
    )


def get_finish_keyboard():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Показать результат", callback_data="show_result")],
            [InlineKeyboardButton("Пройти тест заново", callback_data="restart_test")],
        ]
    )


def build_finish_text(total_questions):
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


def get_next_test_key(user_id, current_test_key=None):
    results = get_user_results(user_id)
    completed = set(results.keys())

    for key in TEST_SEQUENCE:
        if key == current_test_key:
            continue
        if key not in completed:
            return key

    return None


def get_continue_keyboard(next_test_key):
    if not next_test_key:
        return None

    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "➡️ Продолжить",
                    callback_data=f"next:{next_test_key}",
                )
            ]
        ]
    )


def build_continue_text(next_test_key):
    label = TEST_BUTTON_LABELS.get(next_test_key, "Следующий тест")
    return (
        "➡️ Продолжить исследование\n\n"
        f"Следующий тест: *{label}*"
    )


async def send_intro_screen(update, context, test_key: str, test_def):
    chat_id = update.effective_chat.id

    context.user_data["test"] = test_key
    context.user_data["stage"] = "intro"
    context.user_data["index"] = 0
    context.user_data["answers"] = []
    context.user_data["test_message_id"] = None

    await context.bot.send_message(
        chat_id=chat_id,
        text=test_def["intro_text"],
        reply_markup=get_intro_keyboard(test_key),
        parse_mode="Markdown",
    )


async def send_question(update, context, test_def, index: int):
    chat_id = update.effective_chat.id
    question = test_def["questions"][index]

    text = build_question_text(test_def["title"], test_def["questions"], index)
    keyboard = get_question_keyboard(question)

    msg = await context.bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=keyboard,
    )

    context.user_data["test_message_id"] = msg.message_id


async def start_test(update, context, test_key: str, test_def):
    await send_intro_screen(update, context, test_key, test_def)


async def begin_test(update, context, test_key: str, test_def):
    context.user_data["test"] = test_key
    context.user_data["stage"] = "questions"
    context.user_data["index"] = 0
    context.user_data["answers"] = []
    context.user_data["test_message_id"] = None

    await send_question(update, context, test_def, 0)


async def send_result_and_continue(update, context, main_menu_markup, test_def, result_text, share_text):
    user = update.effective_user
    user_id = user.id if user else "unknown"
    chat_id = update.effective_chat.id

    result_keyboard = get_share_keyboard(share_text) if share_text else None

    await context.bot.send_message(
        chat_id=chat_id,
        text=result_text,
        parse_mode="Markdown",
        reply_markup=result_keyboard,
    )

    results_after_save = get_user_results(user_id)
    fresh_main_menu = get_dynamic_main_menu(user_id)

    if has_full_access(results_after_save):
        await context.bot.send_message(
            chat_id=chat_id,
            text=render_basic_code_ready_text(),
            parse_mode="Markdown",
            reply_markup=render_basic_code_ready_keyboard(),
        )
        return

    next_test_key = get_next_test_key(user_id, test_def["key"])
    continue_keyboard = get_continue_keyboard(next_test_key)

    if continue_keyboard:
        await context.bot.send_message(
            chat_id=chat_id,
            text=build_continue_text(next_test_key),
            parse_mode="Markdown",
            reply_markup=continue_keyboard,
        )
        return

    await context.bot.send_message(
        chat_id=chat_id,
        text="Исследование завершено.",
        reply_markup=fresh_main_menu,
    )


async def handle_callback(update, context, main_menu_markup, tests):
    query = update.callback_query
    await query.answer()

    data = query.data
    current_test = context.user_data.get("test")

    if data == "main_menu":
        context.user_data.clear()

        try:
            await query.edit_message_reply_markup(reply_markup=None)
        except Exception:
            pass

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Начните исследование.",
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

        try:
            await query.edit_message_reply_markup(reply_markup=None)
        except Exception:
            pass

        await begin_test(update, context, test_key, tests[test_key])
        return

    if data.startswith("next:"):
        test_key = data.split(":", 1)[1]

        if test_key not in tests:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Этот тест сейчас недоступен.",
                reply_markup=main_menu_markup,
            )
            return

        try:
            await query.edit_message_reply_markup(reply_markup=None)
        except Exception:
            pass

        await send_intro_screen(update, context, test_key, tests[test_key])
        return

    if data == "show_basic_code":
        user = update.effective_user
        user_id = user.id if user else "unknown"
        results = get_user_results(user_id)

        if not enough_for_basic_personality_code(results):
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Сначала завершите три базовых теста.",
                reply_markup=main_menu_markup,
            )
            return

        payload = build_basic_personality_code(results)
        rendered = render_basic_personality_code(payload)

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=rendered,
            parse_mode="Markdown",
        )

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=render_upsell_text(),
            parse_mode="Markdown",
            reply_markup=render_upsell_keyboard(),
        )
        return

    if data == "full_profile_info":
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=(
                "🔒 *ПОЛНЫЙ ПРОФИЛЬ ЛИЧНОСТИ*\n\n"
                "Полный профиль пока находится в разработке.\n\n"
                "Скоро здесь появится расширенная версия системы «Код личности» "
                "с дополнительными тестами и более глубокой интерпретацией."
            ),
            parse_mode="Markdown",
        )
        return

    if not current_test or current_test not in tests:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Начните исследование.",
            reply_markup=main_menu_markup,
        )
        return

    test_def = tests[current_test]

    if data == "restart_test":
        context.user_data["index"] = 0
        context.user_data["answers"] = []
        context.user_data["stage"] = "questions"
        context.user_data["test_message_id"] = None

        try:
            await query.edit_message_reply_markup(reply_markup=None)
        except Exception:
            pass

        await send_question(update, context, test_def, 0)
        return

    if data == "show_result":
        answers = context.user_data.get("answers", [])

        result_payload = test_def["build_result"](answers)

        if isinstance(result_payload, dict):
            result_text = result_payload.get("text", "")
            share_text = result_payload.get("share_text")
        else:
            result_text = result_payload
            share_text = None

        user = update.effective_user
        if user:
            save_user_result(
                user_id=user.id,
                test_key=test_def["key"],
                title=test_def["title"],
                result_text=result_text,
                profile_payload=(
                    test_def["build_profile_payload"](answers)
                    if "build_profile_payload" in test_def
                    else None
                ),
            )

        context.user_data.clear()

        try:
            await query.edit_message_reply_markup(reply_markup=None)
        except Exception:
            pass

        await send_result_and_continue(
            update,
            context,
            main_menu_markup,
            test_def,
            result_text,
            share_text,
        )
        return

    if not data.startswith("ans:"):
        return

    index = context.user_data.get("index", 0)
    current_question = test_def["questions"][index]

    option_index = int(data.split(":")[1])

    if option_index < 0 or option_index >= len(current_question["options"]):
        await query.answer("Такого варианта нет", show_alert=False)
        return

    selected_option = current_question["options"][option_index]
    answer_value = test_def["get_option_value"](selected_option)
    answer_text = test_def["get_option_text"](selected_option)

    question_text = build_question_text(
        test_def["title"],
        test_def["questions"],
        index,
    )

    selected_view = (
    f"{question_text}\n\n"
    f"✅ {answer_text}"
)

    await query.edit_message_text(
        text=selected_view,
        parse_mode="Markdown",
    )

    context.user_data["answers"].append(answer_value)
    context.user_data["index"] = index + 1

    await asyncio.sleep(0.4)

    new_index = context.user_data["index"]

    if new_index >= len(test_def["questions"]):
        context.user_data["stage"] = "finished"

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=build_finish_text(len(test_def["questions"])),
            reply_markup=get_finish_keyboard(),
        )
        return

    await send_question(
        update,
        context,
        test_def,
        new_index,
    )
