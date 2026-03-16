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
from storage.results_store import get_user_results, delete_user_results
from intro.research_intro import research_intro_text, research_intro_keyboard

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 5750354905

if not TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")


ONBOARDING_MENU = [
    ["Начать исследование"],
    ["Мои результаты"],
    ["О тесте"],
]

FULL_MENU = [
    ["Архетип личности"],
    ["Код Тени"],
    ["Уровень внутреннего напряжения"],
    ["Мои результаты"],
    ["Получить Код личности"],
    ["О тесте"],
]

BUTTON_TO_TEST_KEY = {
    "Архетип личности": "archetype",
    "Код Тени": "shadow",
    "Уровень внутреннего напряжения": "anxiety",
}


def is_admin(user_id) -> bool:
    return str(user_id) == str(ADMIN_ID)


def has_full_access(results: dict) -> bool:
    required = {"shadow", "archetype", "anxiety"}
    return required.issubset(set(results.keys()))


def get_main_menu_by_results(results: dict, user_id):
    menu = FULL_MENU if has_full_access(results) else ONBOARDING_MENU
    menu = [row[:] for row in menu]

    if is_admin(user_id):
        menu.append(["Сбросить мои тесты"])

    return ReplyKeyboardMarkup(menu, resize_keyboard=True)


def build_results_text(results: dict) -> str:
    if not results:
        return (
            "У вас пока нет сохранённых результатов.\n\n"
            "Начните исследование, и результаты появятся здесь."
        )

    lines = ["*Мои результаты*\n"]
    ordered_keys = ["archetype", "shadow", "anxiety"]

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
    user_id = user.id if user else "unknown"
    results = get_user_results(user_id)

    await update.message.reply_text(
        "Добро пожаловать в систему «Код личности».",
        reply_markup=get_main_menu_by_results(results, user_id),
    )

    if not has_full_access(results):
        await update.message.reply_text(
            research_intro_text(),
            parse_mode="Markdown",
            reply_markup=research_intro_keyboard(),
        )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    user = update.effective_user
    user_id = user.id if user else "unknown"
    results = get_user_results(user_id)
    main_menu_markup = get_main_menu_by_results(results, user_id)

    if text == "Сбросить мои тесты":
        if not is_admin(user_id):
            await update.message.reply_text(
                "Эта функция доступна только админу.",
                reply_markup=main_menu_markup,
            )
            return

        delete_user_results(user_id)
        context.user_data.clear()

        fresh_results = get_user_results(user_id)
        fresh_menu = get_main_menu_by_results(fresh_results, user_id)

        await update.message.reply_text(
            "Ваши результаты удалены. Теперь бот снова считает вас новым пользователем.",
            reply_markup=fresh_menu,
        )
        return

    if text == "Мои результаты":
        context.user_data.clear()
        await update.message.reply_text(
            build_results_text(results),
            reply_markup=main_menu_markup,
            parse_mode="Markdown",
        )
        return

    if text == "Получить Код личности":
        await update.message.reply_text(
            "Код личности открывается после завершения трёх тестов.",
            reply_markup=main_menu_markup,
        )
        return

    if text == "О тесте":
        context.user_data.clear()

        if has_full_access(results):
            about_text = (
                "Это бот психологических тестов.\n\n"
                "Внутри доступны:\n"
                "• Архетип личности\n"
                "• Код Тени\n"
                "• Уровень внутреннего напряжения\n\n"
                "После прохождения трёх тестов вы можете получить «Код личности».\n\n"
                "Все результаты сохраняются в разделе «Мои результаты»."
            )
        else:
            about_text = (
                "Это бот психологических тестов.\n\n"
                "Вы проходите три теста по цепочке:\n"
                "• Архетип личности\n"
                "• Код Тени\n"
                "• Уровень внутреннего напряжения\n\n"
                "После этого бот собирает результаты в «Код личности».\n\n"
                "Все результаты сохраняются в разделе «Мои результаты»."
            )

        await update.message.reply_text(
            about_text,
            reply_markup=main_menu_markup,
        )
        return

    if text == "Начать исследование":
        context.user_data.clear()
        await start_test(update, context, "archetype", TESTS["archetype"])
        return

    if text in BUTTON_TO_TEST_KEY:
        test_key = BUTTON_TO_TEST_KEY[text]
        context.user_data.clear()

        if has_full_access(results):
            await start_test(update, context, test_key, TESTS[test_key])
        else:
            await update.message.reply_text(
                "Сначала начните исследование. Порядок тестов: Архетип → Код Тени → Уровень внутреннего напряжения.",
                reply_markup=main_menu_markup,
            )
        return

    current_test = context.user_data.get("test")
    if current_test:
        await handle_nav_text(update, context, main_menu_markup, TESTS)
        return

    await update.message.reply_text(
        "Используйте кнопки меню ниже.",
        reply_markup=main_menu_markup,
    )


async def handle_all_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id if user else "unknown"
    results = get_user_results(user_id)
    main_menu_markup = get_main_menu_by_results(results, user_id)
    await handle_callback(update, context, main_menu_markup, TESTS)


def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_all_callbacks))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()


if __name__ == "__main__":
    main()
