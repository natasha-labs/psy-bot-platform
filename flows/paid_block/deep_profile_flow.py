import asyncio
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from tests.deep_profile.test_def import TEST_DEF
from storage.results_store import save_deep_profile_result
from flows.paid_block.paid_access import has_paid_access


def get_paid_question_keyboard(options):
    rows = []
    for index, option in enumerate(options):
        rows.append(
            [InlineKeyboardButton(option["text"], callback_data=f"paid_ans:{index}")]
        )
    return InlineKeyboardMarkup(rows)


def build_paid_question_text(question: dict, index: int, total: int) -> str:
    return (
        f"{question['text']}\n\n"
        f"*Глубокий профиль*\n"
        f"Вопрос {index + 1} / {total}"
    )


async def start_deep_profile(update, context):
    user = update.effective_user
    user_id = user.id if user else "unknown"

    if not has_paid_access(user_id):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Нет доступа к платному блоку.",
        )
        return

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


async def handle_paid_callback(update, context):
    query = update.callback_query
    await query.answer()

    data = query.data
    user = update.effective_user
    user_id = user.id if user else "unknown"

    if data == "paid_start_deep_profile":
        try:
            await query.edit_message_reply_markup(reply_markup=None)
        except Exception:
            pass
        await start_deep_profile(update, context)
        return

    if not data.startswith("paid_ans:"):
        return

    index = context.user_data.get("paid_index", 0)
    questions = TEST_DEF["questions"]
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

    await asyncio.sleep(0.35)

    if context.user_data["paid_index"] >= len(questions):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Анализируем ваши ответы...",
        )

        result_payload = TEST_DEF["build_result"](
            context.user_data["paid_answers"],
            user_id,
        )

        save_deep_profile_result(
            user_id=user_id,
            result_payload=result_payload,
            answers=context.user_data["paid_answers"],
            signal_map=result_payload.get("signals", {}),
            primary_pattern=result_payload.get("primary_pattern"),
            secondary_pattern=result_payload.get("secondary_pattern"),
        )

        context.user_data.pop("paid_test_key", None)
        context.user_data.pop("paid_index", None)
        context.user_data.pop("paid_answers", None)

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=result_payload["text"],
        )
        return

    await send_paid_question(update, context, context.user_data["paid_index"])
