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

from engine.test_engine import (
    send_entry_screen,
    send_test_selection_screen,
    handle_callback,
)
from tests.registry import TESTS
from storage.results_store import get_user_results, delete_user_results

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 5750354905

if not TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")


MAIN_MENU = [
    ["Начать исследование"],
    ["Мои результаты"],
    ["О тесте"],
]


def is_admin(user_id) -> bool:
    return str(user_id) == str(ADMIN_ID)


def get_main_menu(user_id):
    menu = [row[:] for row in MAIN_MENU]

    if is_admin(user_id):
        menu.append(["Сбросить мои тесты"])

    return ReplyKeyboardMarkup(menu, resize_keyboard=True)


def build_results_text(results: dict) -> str:
    if not results:
        return (
            "У вас пока нет сохранённых результатов.\n\n"
            "Начните исследование."
        )

    ordered_keys = ["anxiety", "archetype", "shadow"]
    lines = ["*Мои результаты*\n"]

    for key in ordered_keys:
        if key not in results:
            continue

        item = results[key]
        lines.append(f"*{item['title']}*")
        lines.append(item["result_text"])
        lines.append("━━━━━━━━━━━━━━")

    return "\n".join(lines).strip()


def build_about_text() -> str:
    return (
        "Это система коротких психологических тестов.\n\n"
        "Внутри доступны:\n"
        "• Тревога\n"
        "• Архетип личности\n"
        "• Теневой профиль\n\n"
        "Тесты дают быстрый инсайт и помогают увидеть ваш внутренний код."
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()

    user = update.effective_user
    user_id = user.id if user else "unknown"

    await send_entry_screen(
        update=update,
        context=context,
        main_menu_markup=get_main_menu(user_id),
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    user = update.effective_user
    user_id = user.id if user else "unknown"
    results = get_user_results(user_id)
    main_menu_markup = get_main_menu(user_id)

    if text == "Сбросить мои тесты":
        if not is_admin(user_id):
            await update.message.reply_text(
                "Эта функция доступна только админу.",
                reply_markup=main_menu_markup,
            )
            return

        delete_user_results(user_id)
        context.user_data.clear()

        await update.message.reply_text(
            "Ваши результаты удалены.",
            reply_markup=main_menu_markup,
        )
        return

    if text == "Начать исследование":
        context.user_data.clear()
        await send_test_selection_screen(update, context, main_menu_markup)
        return

    if text == "Мои результаты":
        context.user_data.clear()
        await update.message.reply_text(
            build_results_text(results),
            reply_markup=main_menu_markup,
            parse_mode="Markdown",
        )
        return

    if text == "О тесте":
        context.user_data.clear()
        await update.message.reply_text(
            build_about_text(),
            reply_markup=main_menu_markup,
        )
        return

    await update.message.reply_text(
        "Используйте кнопки меню ниже.",
        reply_markup=main_menu_markup,
    )


async def handle_all_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id if user else "unknown"
    main_menu_markup = get_main_menu(user_id)

    await handle_callback(update, context, main_menu_markup, TESTS)


def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_all_callbacks))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()


if __name__ == "__main__":
    main()
