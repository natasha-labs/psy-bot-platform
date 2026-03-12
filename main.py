from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from engine.runner import run_test

TOKEN = "8691203465:AAEpm9I_xLJQXORp7OQJwiPdEI4UNn2AXWU"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "Добро пожаловать в систему 'Код личности'\n\n"
        "Скоро здесь появятся психологические тесты."
    )


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))

app.run_polling()
