import asyncio
import random
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from storage.results_store import save_user_result, get_user_results
from personality_code.aggregator import (
    enough_for_basic_personality_code,
    build_basic_personality_code,
)
from personality_code.renderer import render_basic_personality_code
from personality_code.upsell_screen import get_learn_more_keyboard

TEST_ORDER = ["anxiety", "archetype", "shadow"]


def select_random_questions(question_bank, count=15):
    if len(question_bank) <= count:
        return question_bank[:]
    return random.sample(question_bank, count)


def get_entry_keyboard():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Начать исследование", callback_data="choose_test_menu")]
        ]
    )


def get_question_keyboard(scale):
    rows = []
    for text, value in scale:
        rows.append([InlineKeyboardButton(text, callback_data=f"ans:{value}")])
    return InlineKeyboardMarkup(rows)


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


def get_continue_keyboard():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Пройти следующий тест", callback_data="next_test")]
        ]
    )


def get_remaining_tests(results):
    completed = set(results.keys())
    return [key for key in TEST_ORDER if key not in completed]


def build_question_text(title: str, total: int, index: int, question_text: str) -> str:
    current = index + 1
    return (
        f"*{title}*\n"
        f"Вопрос {current} / {total}\n\n"
        f"{question_text}"
    )


async def send_entry_screen(update, context, main_menu_markup):
    await send_test_selection_screen(update, context)


async def send_test_selection_screen(update, context, results=None):
    available = None

    if results is not None:
        available = get_remaining_tests(results)

    if available is not None and len(available) == 1:
        text = "Остался последний тест"
    else:
        text = "Выбери, с чего начать:"

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=get_test_selection_keyboard(available),
    )


async def begin_test(update, context, test_key: str, test_def):
    context.user_data["test"] = test_key
    context.user_data["index"] = 0
    context.user_data["answers"] = []
    context.user_data["questions"] = select_random_questions(test_def["question_bank"], 15)
    context.user_data["last_question_message_id"] = None

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

    msg = await context.bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode="Markdown",
        reply_markup=get_question_keyboard(test_def["scale"]),
    )
    context.user_data["last_question_message_id"] = msg.message_id


async def send_post_result_flow(update, context, main_menu_markup, test_def, result_text, profile_payload):
    chat_id = update.effective_chat.id
    user = update.effective_user
    user_id = user.id if user else "unknown"
    test_key = test_def["key"]

    save_user_result(
        user_id=user_id,
        test_key=test_key,
        title=test_def["title"],
        result_text=result_text,
        profile_payload=profile_payload,
    )

    results = get_user_results(user_id)
    remaining = get_remaining_tests(results)

    # После 1 и 2 теста
    if remaining:
        await context.bot.send_message(
            chat_id=chat_id,
            text=result_text,
            parse_mode="Markdown",
        )

        await context.bot.send_message(
            chat_id=chat_id,
            text="Продолжить исследование и собрать полный код личности",
            reply_markup=get_continue_keyboard(),
        )
        return

    # После 3 тестов
    if enough_for_basic_personality_code(results):
        # Сначала показываем результат последнего теста
        await context.bot.send_message(
            chat_id=chat_id,
            text=result_text,
            parse_mode="Markdown",
        )

        payload = build_basic_personality_code(results)
        code_text = render_basic_personality_code(payload)

        final_text = (
            f"{code_text}\n\n"
            "Ты увидел только верхний слой.\n\n"
            "А дальше начинается то, ради чего сюда приходят — пространство для самоисследования."
        )

        await context.bot.send_message(
            chat_id=chat_id,
            text=final_text,
            parse_mode="Markdown",
            reply_markup=get_learn_more_keyboard(),
        )
        return

    await context.bot.send_message(
        chat_id=chat_id,
        text=result_text,
        parse_mode="Markdown",
        reply_markup=main_menu_markup,
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
        return

    if data == "full_profile_info":
        return

    if data == "learn_more":
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
    selected_view = f"{question_text}\n✅ {answer_text}"

    try:
        await query.edit_message_text(
            text=selected_view,
            parse_mode="Markdown",
        )
    except Exception:
        pass

    context.user_data["answers"].append((current_question, answer_value))
    context.user_data["index"] += 1

    await asyncio.sleep(0.35)

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
