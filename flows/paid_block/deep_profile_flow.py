import asyncio
from tests.deep_profile.test_def import TEST_DEF
from flows.paid_block.deep_result_builder import build_deep_result

user_answers = {}

async def handle_paid_callback(update, context):
    query = update.callback_query
    await query.answer()

    if query.data == "start_deep_profile":
        user_answers[query.from_user.id] = []
        await send_question(query, context, 0)

    elif query.data.startswith("dp_"):
        _, q_index, value = query.data.split("|")
        q_index = int(q_index)

        user_answers[query.from_user.id].append(value)

        if q_index + 1 < len(TEST_DEF):
            await send_question(query, context, q_index + 1)
        else:
            await query.message.reply_text("Анализируем твои ответы...")
            await asyncio.sleep(1.5)

            result = build_deep_result(user_answers[query.from_user.id], context)

            await query.message.reply_text(result["part1"])
            await query.message.reply_text(result["part2"])
            await query.message.reply_text(result["part3"])
            await query.message.reply_text(result["part4"])

async def send_question(query, context, index):
    question = TEST_DEF[index]

    buttons = []
    for option in question["options"]:
        buttons.append([
            InlineKeyboardButton(
                option["text"],
                callback_data=f"dp_{index}|{option['type']}"
            )
        ])

    from telegram import InlineKeyboardMarkup
    await query.message.reply_text(
        question["question"],
        reply_markup=InlineKeyboardMarkup(buttons)
    )
