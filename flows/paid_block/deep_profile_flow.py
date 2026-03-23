import asyncio
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from tests.deep_profile.test_def import TEST_DEF
from storage.results_store import (
    save_deep_profile_result,
    mark_deep_profile_started,
)
from flows.paid_block.paid_access import has_paid_access


def get_paid_question_keyboard(options):
    rows = []
    for index, option in enumerate(options):
        rows.append([InlineKeyboardButton(option["text"], callback_data=f"paid_ans:{index}")])
    return InlineKeyboardMarkup(rows)


def get_final_keyboard():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Перейти к ежедневной работе с собой", callback_data="paid_daily_work")],
            [InlineKeyboardButton("Пройти разбор заново", callback_data="paid_restart")],
            [InlineKeyboardButton("Назад", callback_data="paid_back")],
        ]
    )


def build_paid_question_text(question: dict, index: int, total: int) -> str:
    return (
        f"*Глубокий профиль*\n"
        f"Вопрос {index + 1} / {total}\n\n"
        f"*{question['text']}*"
    )


async def start_deep_profile(update, context):
    user = update.effective_user
    user_id = user.id if user else "unknown"

    if not has_paid_access(user_id):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Нет доступа ко второму блоку. Сначала нужна оплата.",
        )
        return

    mark_deep_profile_started(user_id, True)

    context.user_data["paid_test_key"] = TEST_DEF["key"]
    context.user_data["paid_index"] = 0
    context.user_data["paid_answers"] = []

    await send_paid_question(update, context, 0)


async def send_paid_question(update, context, index: int):
    questions = TEST_DEF["questions"]
    question = questions[index]

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=build_paid_question_text(question, index, len(questions)),
        parse_mode="Markdown",
        reply_markup=get_paid_question_keyboard(question["options"]),
    )


async def send_deep_result(chat_id, context, result_payload):
    await context.bot.send_message(chat_id=chat_id, text=result_payload["part1"])
    await context.bot.send_message(chat_id=chat_id, text=result_payload["part2"])
    await context.bot.send_message(
        chat_id=chat_id,
        text=result_payload["part3"],
        reply_markup=get_final_keyboard(),
    )


async def handle_paid_callback(update, context):
    query = update.callback_query
    await query.answer()

    data = query.data
    user = update.effective_user
    user_id = user.id if user else "unknown"

    if data == "paid_start":
        try:
            await query.edit_message_reply_markup(reply_markup=None)
        except Exception:
            pass
        await start_deep_profile(update, context)
        return

    if data == "paid_start_deep_profile":
        try:
            await query.edit_message_reply_markup(reply_markup=None)
        except Exception:
            pass
        await start_deep_profile(update, context)
        return

    if data == "paid_restart":
        try:
            await query.edit_message_reply_markup(reply_markup=None)
        except Exception:
            pass
        await start_deep_profile(update, context)
        return

    if data == "paid_back":
        try:
            await query.edit_message_reply_markup(reply_markup=None)
        except Exception:
            pass
        from flows.paid_block.paid_entry import send_paid_entry
        await send_paid_entry(update, context)
        return

    if data == "paid_daily_work":
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Переход к ежедневной работе с собой будет следующим модулем.",
        )
        return

    if not data.startswith("paid_ans:"):
        return

    if not has_paid_access(user_id):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Нет доступа ко второму блоку. Сначала нужна оплата.",
        )
        return

    index = context.user_data.get("paid_index", 0)
    questions = TEST_DEF["questions"]

    if index >= len(questions):
        return

    question = questions[index]
    option_index = int(data.split(":")[1])
    option = question["options"][option_index]

    try:
        await query.edit_message_text(
            text=f"{question['text']}\n✅ {option['text']}",
        )
    except Exception:
        pass

    context.user_data["paid_answers"].append(
        {
            "question_id": question["id"],
            "question_text": question["text"],
            "option_text": option["text"],
            "value": option["value"],
        }
    )

    context.user_data["paid_index"] = index + 1

    await asyncio.sleep(0.4)

    if context.user_data["paid_index"] >= len(questions):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Анализируем твои ответы…",
        )

        await asyncio.sleep(1.2)

        answers = context.user_data.get("paid_answers", [])
        result_payload = TEST_DEF["build_result"](user_id, answers)

        save_deep_profile_result(
            user_id=user_id,
            result_payload=result_payload,
            answers=answers,
            signal_map=result_payload.get("scores", {}),
            primary_pattern=result_payload.get("main_pattern"),
            secondary_pattern=result_payload.get("second_pattern"),
            behavior_modifier=None,
        )

        context.user_data.pop("paid_test_key", None)
        context.user_data.pop("paid_index", None)
        context.user_data.pop("paid_answers", None)

        await send_deep_result(update.effective_chat.id, context, result_payload)
        return

    await send_paid_question(update, context, context.user_data["paid_index"])
