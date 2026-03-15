import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
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


ONBOARDING_MENU = [
    ["Начать исследование"],
    ["Мои результаты"],
    ["О тесте"],
]

FULL_MENU = [
    ["Код Тени"],
    ["Архетип личности"],
    ["Уровень тревоги"],
    ["Мои результаты"],
    ["О тесте"],
]

BUTTON_TO_TEST_KEY = {
    "Код Тени": "shadow",
    "Архетип личности": "archetype",
    "Уровень тревоги": "anxiety",
}


def has_full_access(results: dict) -> bool:
    required = {"shadow", "archetype", "anxiety"}
    return required.issubset(set(results.keys()))


def get_main_menu_by_results(results: dict):
    menu = FULL_MENU if has_full_access(results) else ONBOARDING_MENU
    return ReplyKeyboardMarkup(menu, resize_keyboard=True)


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

    user = update.effective_user
    results = get_user_results(user.id if user else "unknown")

    await update.message.reply_text(
        "Добро пожаловать в систему «Код личности».",
        reply_markup=get_main_menu_by_results(results),
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    current_test = context.user_data.get("test")

    user = update.effective_user
    user_id = user.id if user else "unknown"
    results = get_user_results(user_id)
    main_menu_markup = get_main_menu_by_results(results)

    if current_test:
        await handle_nav_text(update, context, main_menu_markup, TESTS)
        return

    if text == "Начать исследование":
        await start_test(update, context, "shadow", TESTS["shadow"])
        return

    if text in BUTTON_TO_TEST_KEY:
        test_key = BUTTON_TO_TEST_KEY[text]

        if has_full_access(results):
            await start_test(update, context, test_key, TESTS[test_key])
        else:
            await update.message.reply_text(
                "Сначала начните исследование с теста «Код Тени».",
                reply_markup=main_menu_markup,
            )
        return

    if text == "Мои результаты":
        await update.message.reply_text(
            build_results_text(results),
            reply_markup=main_menu_markup,
            parse_mode="Markdown",
        )
        return

    if text == "О тесте":
        if has_full_access(results):
            about_text = (
                "Это бот психологических тестов.\n\n"
                "Внутри доступны:\n"
                "• Код Тени\n"
                "• Архетип личности\n"
                "• Уровень тревоги\n\n"
                "Все результаты сохраняются в разделе «Мои результаты»."
            )
        else:
            about_text = (
                "Это бот психологических тестов.\n\n"
                "Сначала вы проходите «Код Тени», а затем бот предлагает "
                "следующие тесты по цепочке исследования.\n\n"
                "Все результаты сохраняются в разделе «Мои результаты»."
            )

        await update.message.reply_text(
            about_text,
            reply_markup=main_menu_markup,
        )
        return

    await update.message.reply_text(
        "Используйте кнопки меню ниже.",
        reply_markup=main_menu_markup,
    )


async def handle_all_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    results = get_user_results(user.id if user else "unknown")
    main_menu_markup = get_main_menu_by_results(results)
    await handle_callback(update, context, main_menu_markup, TESTS)


def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CallbackQueryHandler(handle_all_callbacks))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()


if __name__ == "__main__":
    main()
