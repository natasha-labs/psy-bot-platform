result = TEST_DEF["build_result"](user_id, answers)

await query.message.reply_text(result["part1"])
await query.message.reply_text(result["part2"])

keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton("Перейти к ежедневной работе с собой", callback_data="final_cta")],
    [InlineKeyboardButton("Пройти разбор заново", callback_data="paid_restart")],
    [InlineKeyboardButton("Назад", callback_data="paid_back")]
])

await query.message.reply_text(result["part3"], reply_markup=keyboard)
