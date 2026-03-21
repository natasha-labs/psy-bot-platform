import asyncio
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from tests.deep_profile.test_def import TEST_DEF
from storage.results_store import (
    save_deep_profile_result,
    mark_deep_profile_started,
)
from flows.paid_block.paid_access import has_paid_access


BEHAVIOR_QUESTION_TEXT = "Когда становится напряжённо, что происходит чаще всего?"

BEHAVIOR_OPTIONS = [
    ("Я замыкаюсь и ухожу в себя", "FREEZE"),
    ("Я стараюсь отвлечься или уйти от ситуации", "ESCAPE"),
    ("Я могу резко среагировать", "OUTBURST"),
    ("Я начинаю всё контролировать ещё сильнее", "OVERCONTROL"),
    ("Я подстраиваюсь под других, чтобы избежать конфликта", "PEOPLE_PLEASING"),
]


def get_paid_question_keyboard(options):
    rows = []
    for index, option in enumerate(options):
        rows.append([InlineKeyboardButton(option["text"], callback_data=f"paid_ans:{index}")])
    return InlineKeyboardMarkup(rows)


def get_behavior_keyboard():
    rows = []
    for index, (text, _) in enumerate(BEHAVIOR_OPTIONS):
        rows.append([InlineKeyboardButton(text, callback_data=f"paid_behavior:{index}")])
    return InlineKeyboardMarkup(rows)


def build_paid_question_text(question: dict, index: int, total: int) -> str:
    return (
        f"*Глубокий профиль*\n"
        f"Вопрос {index + 1} / {total}\n\n"
        f"*{question['text']}*"
    )


def split_long_text(text: str, limit: int = 3500):
    parts = []
    current = ""

    for block in text.split("\n\n"):
        candidate = block if not current else f"{current}\n\n{block}"
        if len(candidate) <= limit:
            current = candidate
        else:
            if current:
                parts.append(current)
            if len(block) <= limit:
                current = block
            else:
                # если отдельный блок слишком длинный — режем жёстко
                chunk = ""
                for line in block.split("\n"):
                    candidate_line = line if not chunk else f"{chunk}\n{line}"
                    if len(candidate_line) <= limit:
                        chunk = candidate_line
                    else:
                        if chunk:
                            parts.append(chunk)
                        chunk = line
                current = chunk

    if current:
        parts.append(current)

    return parts


async def send_result_chunks(chat_id, context, text: str):
    chunks = split_long_text(text)
    for chunk in chunks:
        await context.bot.send_message(
            chat_id=chat_id,
            text=chunk,
        )


async def start_deep_profile(update, context):
    user = update.effective_user
    user_id = user.id if user else "unknown"

    if not has_paid_access(user_id):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Нет доступа к платному блоку. Сначала нужна оплата.",
        )
        return

    mark_deep_profile_started(user_id, True)

    context.user_data["paid_test_key"] = TEST_DEF["key"]
    context.user_data["paid_index"] = 0
    context.user_data["paid_answers"] = []
    context.user_data["behavior_modifier"] = None

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


async def send_behavior_question(update, context):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"*Глубокий профиль*\n\n*{BEHAVIOR_QUESTION_TEXT}*",
        parse_mode="Markdown",
        reply_markup=get_behavior_keyboard(),
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

    if data.startswith("paid_behavior:"):
        if not has_paid_access(user_id):
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Нет доступа ко второму блоку. Сначала нужна оплата.",
            )
            return

        option_index = int(data.split(":")[1])
        option_text, modifier_value = BEHAVIOR_OPTIONS[option_index]
        context.user_data["behavior_modifier"] = modifier_value

        try:
            await query.edit_message_text(
                text=f"{BEHAVIOR_QUESTION_TEXT}\n✅ {option_text}",
            )
        except Exception:
            pass

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Анализируем ваши ответы...",
        )

        await asyncio.sleep(0.8)

        try:
            answers = context.user_data.get("paid_answers", [])

            result_payload = TEST_DEF["build_result"](
                user_id=user_id,
                answers=answers,
                behavior_modifier=modifier_value,
            )

            save_deep_profile_result(
                user_id=user_id,
                result_payload=result_payload,
                answers=answers,
                signal_map=result_payload.get("signals", {}),
                primary_pattern=result_payload.get("primary_pattern"),
                secondary_pattern=result_payload.get("secondary_pattern"),
                behavior_modifier=modifier_value,
            )

            context.user_data.pop("paid_test_key", None)
            context.user_data.pop("paid_index", None)
            context.user_data.pop("paid_answers", None)
            context.user_data.pop("behavior_modifier", None)

            result_text = result_payload.get("text", "Результат собран, но текст пуст.")
            await send_result_chunks(update.effective_chat.id, context, result_text)

        except Exception as e:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Ошибка при сборке результата: {str(e)}",
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
        await send_behavior_question(update, context)
        return

    await send_paid_question(update, context, context.user_data["paid_index"])
