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
        [
            [InlineKeyboardButton("Начать исследование", callback_data="choose_test_menu")]
        ]
    )


def get_test_selection_keyboard(available_tests=None):
    mapping = {
        "anxiety": "Тревога",
        "archetype": "Архетип личности",
        "shadow": "Теневой профиль",
    }

    rows = []
    for key in TEST_ORDER:
        if available_tests is not None and key not in available_tests:
            continue
        rows.append([InlineKeyboardButton(mapping[key], callback_data=f"start:{key}")])

    return InlineKeyboardMarkup(rows)


def get_result_keyboard(test_key: str, button_text: str):
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(button_text, callback_data=f"offer:{test_key}")]
        ]
    )


def get_continue_keyboard():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Пройти следующий тест", callback_data="next_test")]
        ]
    )


def get_question_keyboard(scale):
    rows = []
    for text, value in scale:
        rows.append([InlineKeyboardButton(text, callback_data=f"ans:{value}")])
    return InlineKeyboardMarkup(rows)


def select_random_questions(question_bank, count=15):
    selected = random.sample(question_bank, count)
    random.shuffle(selected)
    return selected


def get_remaining_tests(results):
    completed = set(results.keys())
    return [key for key in TEST_ORDER if key not in completed]


def build_question_text(title: str, total: int, index: int, question_text: str) -> str:
    current = index + 1
    return (
        f"{question_text}\n\n"
        f"*{title}*\n"
        f"Вопрос {current} / {total}"
    )


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


async def send_test_selection_screen(update, context, results=None):
    remaining = None
    if results is not None:
        remaining = get_remaining_tests(results)

    text = "Выбери, с чего начать:" if remaining is None else "Выбери следующий тест:"

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=get_test_selection_keyboard(remaining),
    )


async def begin_test(update, context, test_key: str, test_def):
    context.user_data["test"] = test_key
    context.user_data["index"] = 0
    context.user_data["answers"] = []
    context.user_data["questions"] = select_random_questions(test_def["question_bank"], 15)

    await send_question(update, context, test_def, 0)


async def send_question(update, context, test_def, index: int):
    chat_id = update.effective_chat.id
    questions = context.user_data["questions"]
    question = questions[index]
    question_text = test_def["get_question_text"](question)

    text = build_question_text(
        title=test_def["title"],
        total=len(questions),
        index=index,
        question_text=question_text,
    )

    await context.bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode="Markdown",
        reply_markup=get_question_keyboard(test_def["scale"]),
    )


async def send_post_result_flow(update, context, main_menu_markup, test_def, result_text, profile_payload):
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

    # 1. Главная кнопка (деньги)
    await context.bot.send_message(
        chat_id=chat_id,
        text=result_text,
        parse_mode="Markdown",
        reply_markup=get_result_keyboard(test_key, test_def["result_button_text"]),
    )

    # 2. Вторичный CTA (ПРАВИЛЬНО — В ОДНОМ СООБЩЕНИИ)
    remaining = get_remaining_tests(results)
    if remaining:
        await context.bot.send_message(
            chat_id=chat_id,
            text="Продолжить исследование и собрать полный код личности",
            reply_markup=get_continue_keyboard(),
        )

    # 3. Код личности
    if enough_for_basic_personality_code(results):
        payload = build_basic_personality_code(results)
        code_text = render_basic_personality_code(payload)

        await context.bot.send_message(
            chat_id=chat_id,
            text=code_text,
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
        try:
            await query.edit_message_reply_markup(reply_markup=None)
        except Exception:
            pass

        await send_test_selection_screen(update, context)
        return

    if data == "next_test":
        try:
            await query.edit_message_reply_markup(reply_markup=None)
        except Exception:
            pass

        await send_test_selection_screen(update, context, results=results)
        return

    if data.startswith("start:"):
        test_key = data.split(":", 1)[1]

        if test_key not in tests:
            return

        try:
            await query.edit_message_reply_markup(reply_markup=None)
        except Exception:
            pass

        await begin_test(update, context, test_key, tests[test_key])
        return

    if data.startswith("offer:"):
        test_key = data.split(":", 1)[1]
        test_def = tests.get(test_key)
        if not test_def:
            return

        item = results.get(test_key, {})
        profile_payload = item.get("profile_payload", {})

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=test_def["build_offer_text"](profile_payload),
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

    if not data.startswith("ans:"):
        return

    current_test = context.user_data.get("test")
    if not current_test or current_test not in tests:
        return

    test_def = tests[current_test]
    index = context.user_data["index"]
    questions = context.user_data["questions"]
    current_question = questions[index]

    answer_value = int(data.split(":")[1])

    answer_text = ""
    for text, value in test_def["scale"]:
        if value == answer_value:
            answer_text = text
            break

    question_text = test_def["get_question_text"](current_question)

    try:
        await query.edit_message_text(
            text=f"{question_text}\n\n✅ {answer_text}",
            parse_mode="Markdown",
        )
    except Exception:
        pass

    context.user_data["answers"].append((current_question, answer_value))
    context.user_data["index"] += 1

    await asyncio.sleep(0.3)

    if context.user_data["index"] >= len(questions):
        answer_pairs = context.user_data["answers"]

        result_text = test_def["build_result"](answer_pairs)
        profile_payload = test_def["build_profile_payload"](answer_pairs)

        context.user_data.clear()

        await send_post_result_flow(
            update=update,
            context=context,
            main_menu_markup=main_menu_markup,
            test_def=test_def,
            result_text=result_text,
            profile_payload=profile_payload,
        )
        return

    await send_question(update, context, test_def, context.user_data["index"])
