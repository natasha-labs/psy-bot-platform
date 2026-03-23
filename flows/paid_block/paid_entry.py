from telegram import InlineKeyboardButton, InlineKeyboardMarkup

async def send_paid_entry(update, context):
    text = (
        "Ты уже увидел только поверхность.\n\n"
        "Но сейчас ты не видишь главное:\n\n"
        "👉 что именно управляет твоими решениями\n"
        "👉 где ты теряешь контроль над собой\n"
        "👉 почему одни и те же сценарии повторяются\n\n"
        "Сейчас ты разберёшь:\n\n"
        "— свой реальный внутренний сценарий\n"
        "— механизм, который запускает твои реакции\n"
        "— точку, где ты теряешь себя\n"
        "— и точку, где это можно изменить\n\n"
        "Это не описание.\n\n"
        "👉 Это разбор того, как ты реально живёшь изнутри."
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("👉 Перейти к моему полному разбору", callback_data="start_deep_profile")]
    ])

    await update.message.reply_text(text, reply_markup=keyboard)
