from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
)

from storage.results_store import save_user_result, get_user_results
from personality_code.aggregator import enough_for_basic_personality_code, build_basic_personality_code
from personality_code.renderer import render_basic_personality_code
from personality_code.completion_screen import completion_text, completion_keyboard
from personality_code.upsell_screen import upsell_text, upsell_keyboard

BACK_BUTTON = "⬅️ Назад"
RESTART_BUTTON = "🔄 Пройти тест заново"
TO_TESTS_BUTTON = "◀️ К выбору тестов"

TEST_SEQUENCE = [
    "archetype",
    "shadow",
    "anxiety",
]

TEST_BUTTON_LABELS = {
    "archetype": "Архетип личности",
    "shadow": "Код Тени",
    "anxiety": "Уровень внутреннего напряжения",
}


def get_nav_menu():
    keyboard = [
        [BACK_BUTTON],
        [RESTART_BUTTON],
        [TO_TESTS_BUTTON],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def has_full_access(results: dict) -> bool:
    required = {"shadow", "archetype", "anxiety"}
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


def get_intro_keyboard(test_key: str, button_text: str = "Начать тест"):
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(button_text, callback_data=f"start:{test_key}")],
            [InlineKeyboardButton("Назад", callback_data="main_menu")],
        ]
    )


def build_progress_bar(current, total):
    total_blocks = 10
    filled = max(1, round((current / total) * total_blocks))
    filled = min(filled, total_blocks)
    empty = total_blocks - filled
    return "█" * filled + "░" * empty


def build_question_text(title: str, questions, index: int, get_option_text) -> str:
    question = questions[index]
    total = len(questions)
    current = index + 1
    progress = build_progress_bar(current, total)

    return (
        f"*ТЕСТ: {title.upper()}*\n\n"
        f"Вопрос {current} из {total}\n"
        f"{progress}\n\n"
        f"{question['text']}"
    )


def get_question_keyboard(question):
    rows = []

    for option_index, option in enumerate(question["options"]):
        text = option["text"] if isinstance(option, dict) else option
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


def get_next_test_key(user_id, current_test_key):
    results = get_user_results(user_id)
    completed = set(results.keys())

    if current_test_key not in TEST_SEQUENCE:
        return None

    current_index = TEST_SEQUENCE.index(current_test_key)

    for next_index in range(current_index + 1, len(TEST_SEQUENCE)):
        candidate = TEST_SEQUENCE[next_index]
        if candidate not in completed:
            return candidate

    return None


def get_continue_keyboard(user_id, current_test_key):
    next_test_key = get_next_test_key(user_id, current_test_key)

    if not next_test_key:
        return None

    button_text = TEST_BUTTON_LABELS[next_test_key]

    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(button_text, callback_data=f"next:{next_test_key}")]
        ]
    )


async def send_intro_screen(update, context, test_key: str, test_def):
    chat_id = update.effective_chat.id
    intro_button_text = test_def.get("intro_button_text", "Начать тест")

    context.user_data["test"] = test_key
    context.user_data["stage"] = "intro"
    context.user_data["index"] = 0
    context.user_data["answers"] = []
    context.user_data["test_message_id"] = None

    await context.bot.send_message(
        chat_id=chat_id,
        text=test_def["intro_text"],
        reply_markup=get_intro_keyboard(test_key, intro_button_text),
        parse_mode="Markdown",
    )


async def send_or_edit_question(update, context, test_def, index: int):
    question = test_def["questions"][index]
    question_text = build_question_text(
        test_def["title"],
        test_def["questions"],
        index,
        test_def["get_option_text"],
    )
    keyboard = get_question_keyboard(question)

    chat_id = update.effective_chat.id
    message_id = context.user_data.get("test_message_id")

    if message_id:
        try:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=question_text,
                reply_markup=keyboard,
                parse_mode="Markdown",
            )
            return
        except Exception:
            pass

    msg = await context.bot.send_message(
        chat_id=chat_id,
        text=question_text,
        reply_markup=keyboard,
        parse_mode="Markdown",
    )
    context.user_data["test_message_id"] = msg.message_id


async def start_test(update, context, test_key: str, test_def):
    await send_intro_screen(update, context, test_key, test_def)


async def begin_test(update, context, test_key: str, test_def):
    chat_id = update.effective_chat.id

    context.user_data["test"] = test_key
    context.user_data["stage"] = "questions"
    context.user_data["index"] = 0
    context.user_data["answers"] = []
    context.user_data["test_message_id"] = None

    await context.bot.send_message(
        chat_id=chat_id,
        text=f"*ТЕСТ НАЧАТ*\n\n*{test_def['title'].upper()}*",
        reply_markup=get_nav_menu(),
        parse_mode="Markdown",
    )

    await send_or_edit_question(update, context, test_def, 0)


async def handle_nav_text(update, context, main_menu_markup, tests):
    text = update.message.text
    current_test = context.user_data.get("test")
    stage = context.user_data.get("stage")

    if not current_test or current_test not in tests:
        await update.message.reply_text(
            "Начните исследование.",
            reply_markup=main_menu_markup,
        )
        return

    test_def = tests[current_test]

    if text == BACK_BUTTON:
        if stage == "intro":
            context.user_data.clear()
            await update.message.reply_text(
                "Начните исследование.",
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

        await send_or_edit_question(
            update,
            context,
            test_def,
            context.user_data["index"],
        )
        return

    if text == RESTART_BUTTON:
        if stage != "questions":
            await update.message.reply_text(
                "Сначала нажмите «Начать тест».",
                reply_markup=main_menu_markup,
            )
            return

        context.user_data["index"] = 0
        context.user_data["answers"] = []

        await send_or_edit_question(
            update,
            context,
            test_def,
            0,
        )
        return

    if text == TO_TESTS_BUTTON:
        context.user_data.clear()
        await update.message.reply_text(
            "Начните исследование.",
            reply_markup=main_menu_markup,
        )
        return

    await update.message.reply_text(
        "Для ответа используйте кнопки под вопросом.",
        reply_markup=get_nav_menu() if stage == "questions" else main_menu_markup,
    )


async def send_result_block(chat_id, context, result_text, share_text):
    result_keyboard = get_share_keyboard(share_text) if share_text else None
    await context.bot.send_message(
        chat_id=chat_id,
        text=result_text,
        parse_mode="Markdown",
        reply_markup=result_keyboard,
    )


async def handle_after_test(update, context, main_menu_markup, test_def):
    user = update.effective_user
    user_id = user.id if user else "unknown"
    chat_id = update.effective_chat.id

    user_results = get_user_results(user_id)
    fresh_main_menu = get_dynamic_main_menu(user_id)

    if enough_for_basic_personality_code(user_results):
        await context.bot.send_message(
            chat_id=chat_id,
            text=completion_text(),
            parse_mode="Markdown",
            reply_markup=completion_keyboard(),
        )

        await context.bot.send_message(
            chat_id=chat_id,
            text="Все тесты пройдены. Теперь в меню доступны все тесты, раздел «Мои результаты» и «Получить Код личности».",
            reply_markup=fresh_main_menu,
        )
        return

    continue_keyboard = get_continue_keyboard(user_id, test_def["key"])

    if continue_keyboard:
        await context.bot.send_message(
            chat_id=chat_id,
            text="➡️ *Продолжить исследование*",
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

    if data == "start_research":
        try:
            await query.edit_message_reply_markup(reply_markup=None)
        except Exception:
            pass

        await send_intro_screen(update, context, "archetype", tests["archetype"])
        return

    if data == "show_personality_code":
        user = update.effective_user
        user_id = user.id if user else "unknown"
        user_results = get_user_results(user_id)

        if not enough_for_basic_personality_code(user_results):
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Сначала нужно пройти три базовых теста.",
                reply_markup=main_menu_markup,
            )
            return

        personality_payload = build_basic_personality_code(user_results)

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=render_basic_personality_code(personality_payload),
            parse_mode="Markdown",
        )

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=upsell_text(),
            parse_mode="Markdown",
            reply_markup=upsell_keyboard(),
        )
        return

    if data == "premium_stub":
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Полный код личности будет подключён следующим этапом.",
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

    if not current_test or current_test not in tests:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Начните исследование.",
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
        result_payload = test_def["build_result"](context.user_data["answers"])
        profile_payload = test_def["build_profile_payload"](context.user_data["answers"])

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
                profile_payload=profile_payload,
            )

        context.user_data.clear()

        await send_result_block(
            chat_id=update.effective_chat.id,
            context=context,
            result_text=result_text,
            share_text=share_text,
        )

        await handle_after_test(update, context, main_menu_markup, test_def)
        return

    await send_or_edit_question(
        update,
        context,
        test_def,
        new_index,
    )
