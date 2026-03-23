from tests.deep_profile.test_def import TEST_DEF

async def handle_paid_callback(update, context):
    query = update.callback_query
    data = query.data

    if data == "paid_start":
        context.user_data["paid_index"] = 0
        context.user_data["answers"] = []
        await send_question(update, context)
        return

    if data.startswith("paid_ans:"):
        index = context.user_data["paid_index"]
        question = TEST_DEF["questions"][index]
        option_index = int(data.split(":")[1])
        option = question["options"][option_index]

        context.user_data["answers"].append(option)
        context.user_data["paid_index"] += 1

        if context.user_data["paid_index"] >= len(TEST_DEF["questions"]):
            result = TEST_DEF["build_result"](
                update.effective_user.id,
                context.user_data["answers"]
            )

            await context.bot.send_message(update.effective_chat.id, result["part1"])
            await context.bot.send_message(update.effective_chat.id, result["part2"])
            await context.bot.send_message(update.effective_chat.id, result["part3"])
            return

        await send_question(update, context)


async def send_question(update, context):
    index = context.user_data["paid_index"]
    question = TEST_DEF["questions"][index]

    buttons = [
        [InlineKeyboardButton(opt["text"], callback_data=f"paid_ans:{i}")]
        for i, opt in enumerate(question["options"])
    ]

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=question["text"],
        reply_markup=InlineKeyboardMarkup(buttons)
    )
