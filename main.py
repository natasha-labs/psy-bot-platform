from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler
from flows.paid_block.deep_profile_flow import handle_paid_callback

TOKEN = "YOUR_TOKEN"

async def start(update, context):
    await update.message.reply_text("Старт")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_paid_callback))

    app.run_polling()

if __name__ == "__main__":
    main()
