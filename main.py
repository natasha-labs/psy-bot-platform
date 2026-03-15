import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

from engine.test_engine import start_test, handle_nav_text, handle_callback
from tests.registry import TESTS
from storage.results_store import get_user_results

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")


MAIN_MENU = [
    ["Начать исследование"],
    ["Мои результаты"],
    ["О тесте"],
]


def get_main_menu():
    return ReplyKeyboardMarkup(MAIN_MENU, resize_keyboard=True)


def build_results_text(results: dict) -> str:
    if not results:
        return (
            "У вас пока нет сохранённых результатов.\n\n"
            "Начните исследование, и результаты появятся здесь."
        )

    lines = ["*Мои результаты*\n"]
    ordered_keys = ["shadow", "archetype", "anxiety"]

    for key in ordered_keys:
        if key not in results:
            continue

        item = results[key]
        lines.append(f"*{item['title']}*")
        lines.append(f"Дата: {item['saved_at']}")
        lines.append(item["result_text"])
        lines.append("━━━━━━━━━━━━━━")

    return "\n".join(lines).strip()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "Добро пожаловать в систему «Код личности».\n\n"
        "Начните исследование себя.",
        reply_markup=get_main_menu(),
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    current_test = context.user_data.get("test")

    if current_test:
        await handle_nav_text(update, context, get_main_menu(), TESTS)
        return

    if text == "Начать исследование":
        await start_test(update, context, "shadow", TESTS["shadow"])
        return

    if text == "Мои результаты":
        user = update.effective_user
        results = get_user_results(user.id if user else "unknown")

        await update.message.reply_text(
            build_results_text(results),
            reply_markup=get_main_menu(),
            parse_mode="Markdown",
        )
        return

    if text == "О тесте":
        await update.message.reply_text(
            "Это бот психологических тестов.\n\n"
            "Сначала вы проходите «Код Тени», а затем бот предлагает "
            "следующие тесты по цепочке исследования.\n\n"
            "Внутри доступны:\n"
            "• Код Тени\n"
            "• Архетип личности\n"
            "• Уровень тревоги\n\n"
            "Все результаты сохраняются в разделе «Мои результаты».",
            reply_markup=get_main_menu(),
        )
        return

    await update.message.reply_text(
        "Используйте кнопки меню ниже.",
        reply_markup=get_main_menu(),
    )


async def handle_all_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_callback(update, context, get_main_menu(), TESTS)


def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_all_callbacks))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()


if __name__ == "__main__":
    main()
