from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "8691203465:AAEpm9I_xLJQXORp7OQJwiPdEI4UNn2AXWU"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        ["Код Тени"],
        ["Архетип личности"],
        ["Уровень тревоги"]
    ]

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Добро пожаловать в систему 'Код личности'\n\nВыберите тест:",
        reply_markup=reply_markup
    )


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))

app.run_polling()
