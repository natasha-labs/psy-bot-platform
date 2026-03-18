import asyncio
import random
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from storage.results_store import save_user_result, get_user_results
from personality_code.aggregator import (
    enough_for_basic_personality_code,
    build_basic_personality_code,
)
from personality_code.renderer import render_basic_personality_code
from personality_code.upsell_screen import (
    get_deep_dive_keyboard,
    get_full_profile_keyboard,
    get_payment_placeholder_text,
)

TEST_ORDER = ["anxiety", "archetype", "shadow"]


def get_entry_keyboard():
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("Начать исследование", callback_data="choose_test_menu")]]
    )


def get_test_selection_keyboard(available_tests=None):
    buttons = []

    mapping = {
        "anxiety": "Тревога",
        "archetype": "Архетип личности",
        "shadow": "Теневой профиль",
    }

    for key in TEST_ORDER:
        if available_tests and key not in available_tests:
            continue

        buttons.append([InlineKeyboardButton(mapping[key], callback_data=f"start:{key}")])

    return InlineKeyboardMarkup(buttons)


def get_result_keyboard(test_key: str, button_text: str):
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(button_text, callback_data=f"offer:{test_key}")]]
    )


def get_continue_keyboard():
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("Пройти следующий тест", callback_data="next_test")]]
    )


def get_question_keyboard(scale):
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(text, callback_data=f"ans:{value}")] for text, value in scale]
    )


def select_random_questions(question_bank, count=15):
    selected = random.sample(question_bank, count)
    random.shuffle(selected)
    return selected


def get_remaining_tests(results):
    completed = set(results.keys())
    return [key for key in TEST_ORDER if key not in completed]


async def send_entry_screen(update, context, main_menu_markup):
    await update.message.reply_text(
        "Ты думаешь, что понимаешь себя.\n\n"
        "Но решения, реакции и выборы\n"
        "часто происходят автоматически.\n\n"
        "Внутри тебя есть система,\n"
        "которая управляет этим:\n\n"
        "— как ты реагируешь\n"
        "— что чувствуешь\n"
        "— какие сценарии повторяешь\n\n"
        "Мы собрали короткие тесты,\n"
        "которые покажут твой внутренний код.\n\n"
        "Это займёт 2–3 минуты.",
        reply_markup=main_menu_markup,
    )

    await update.message.reply_text(
        "Начать исследование",
        reply_markup=get_entry_keyboard(),
    )


async def begin_test(update, context, test_key: str, test_def):
    context.user_data["test"] = test_key
    context.user_data["index"] = 0
    context.user_data["answers"] = []
    context.user_data["questions"] = select_random_questions(test_def["question_bank"], 15)

    await send_question(update, context, test_def, 0)


async def send_question(update, context, test_def, index):
    q = context.user_data["questions"][index]

    text = (
        f"{q['text']}\n\n"
        f"*{test_def['title']}*\n"
        f"Вопрос {index+1} / {len(context.user_data['questions'])}"
    )

    msg = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        parse_mode="Markdown",
        reply_markup=get_question_keyboard(test_def["scale"]),
    )

    context.user_data["msg_id"] = msg.message_id


async def send_test_result(update, context, main_menu_markup, test_def, result_text, profile_payload):
    chat_id = update.effective_chat.id
    test_key = test_def["key"]

    user = update.effective_user
    user_id = user.id if user else "unknown"

    save_user_result(
        user_id=user_id,
        test_key=test_key,
        title=test_def["title"],
        result_text=result_text,
        profile_payload=profile_payload,
    )

    results = get_user_results(user_id)

    # 1. результат
    await context.bot.send_message(
        chat_id=chat_id,
        text=result_text,
        parse_mode="Markdown",
        reply_markup=get_result_keyboard(test_key, test_def["result_button_text"]),
    )

    # 2. продолжение воронки
    remaining = get_remaining_tests(results)

    if remaining:
        await context.bot.send_message(
            chat_id=chat_id,
            text="Продолжить исследование и собрать полный код личности",
        )

        await context.bot.send_message(
            chat_id=chat_id,
            text="",
            reply_markup=get_continue_keyboard(),
        )

    # 3. код личности
    if enough_for_basic_personality_code(results):
        payload = build_basic_personality_code(results)

        await context.bot.send_message(
            chat_id=chat_id,
            text=render_basic_personality_code(payload),
            parse_mode="Markdown",
            reply_markup=get_full_profile_keyboard(),
        )


async def handle_callback(update, context, main_menu_markup, tests):
    query = update.callback_query
    await query.answer()
    data = query.data

    user = update.effective_user
    user_id = user.id if user else "unknown"

    results = get_user_results(user_id)

    if data == "choose_test_menu":
        remaining = get_remaining_tests(results)

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Выбери, с чего начать:",
            reply_markup=get_test_selection_keyboard(remaining),
        )
        return

    if data == "next_test":
        remaining = get_remaining_tests(results)

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Выбери следующий тест:",
            reply_markup=get_test_selection_keyboard(remaining),
        )
        return

    if data.startswith("start:"):
        test_key = data.split(":")[1]
        await begin_test(update, context, test_key, tests[test_key])
        return

    if data.startswith("offer:"):
        test_key = data.split(":")[1]
        test_def = tests[test_key]

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=test_def["build_offer_text"]({}),
            parse_mode="Markdown",
            reply_markup=get_deep_dive_keyboard(),
        )
        return

    if data == "full_profile_info":
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=get_payment_placeholder_text(),
            parse_mode="Markdown",
        )
        return

    if data.startswith("ans:"):
        val = int(data.split(":")[1])
        idx = context.user_data["index"]
        q = context.user_data["questions"][idx]

        context.user_data["answers"].append((q, val))
        context.user_data["index"] += 1

        await asyncio.sleep(0.4)

        if context.user_data["index"] >= len(context.user_data["questions"]):
            test_key = context.user_data["test"]
            test_def = tests[test_key]

            answers = context.user_data["answers"]

            result_text = test_def["build_result"](answers)
            payload = test_def["build_profile_payload"](answers)

            context.user_data.clear()

            await send_test_result(update, context, main_menu_markup, test_def, result_text, payload)
            return

        await send_question(update, context, tests[context.user_data["test"]], context.user_data["index"])
