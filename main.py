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

from engine.test_engine import start_test, handle_callback
from tests.registry import TESTS
from storage.results_store import get_user_results, delete_user_results

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
    ["Внутреннее напряжение"],
    ["Мои результаты"],
    ["Получить Код личности"],
    ["О тесте"],
]

BUTTON_TO_TEST_KEY = {
    "Архетип личности": "archetype",
    "Код Тени": "shadow",
    "Внутреннее напряжение": "anxiety",
}


def is_admin(user_id) -> bool:
    return str(user_id) == str(ADMIN_ID)


def has_full_access(results: dict) -> bool:
    required = {"archetype", "shadow", "anxiety"}
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
        lines.append(item["result_text"])
        lines.append("━━━━━━━━━━━━━━")

    return "\n".join(lines).strip()


def build_research_intro_text():
    return (
        "✨ *Как работает исследование*\n\n"
        "Вы пройдёте три коротких теста.\n"
        "Каждый из них раскрывает отдельный слой вашей личности.\n\n"
        "🧭 *Архетип личности*\n"
        "покажет ваш основной способ взаимодействия с людьми и миром.\n\n"
        "🌑 *Теневая сторона*\n"
        "поможет увидеть часть личности, которую обычно трудно заметить.\n\n"
        "⚡ *Уровень внутреннего напряжения*\n"
        "покажет, как стресс и внутренние реакции влияют на ваши решения.\n\n"
        "После каждого теста вы получите короткий результат.\n\n"
        "Когда все три теста будут завершены, система соберёт их в:\n\n"
        "🧬 *КОД ЛИЧНОСТИ*\n\n"
        "Это ваш психологический профиль, который показывает,\n"
        "как соединяются разные части вашей личности.\n\n"
        "*3 теста • примерно 5 минут*"
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()

    user = update.effective_user
    user_id = user.id if user else "unknown"
    results = get_user_results(user_id)
    main_menu_markup = get_main_menu_by_results(results, user_id)

    await update.message.reply_text(
        "Добро пожаловать в систему «Код личности».",
        reply_markup=main_menu_markup,
    )

    if not has_full_access(results):
        await update.message.reply_text(
            build_research_intro_text(),
            parse_mode="Markdown",
            reply_markup=main_menu_markup,
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

    if text == "О тесте":
        context.user_data.clear()

        if has_full_access(results):
            about_text = (
                "Это бот психологических тестов.\n\n"
                "Внутри доступны:\n"
                "• Архетип личности\n"
                "• Код Тени\n"
                "• Внутреннее напряжение\n\n"
                "После прохождения трёх тестов можно получить «Код личности».\n\n"
                "Все результаты сохраняются в разделе «Мои результаты»."
            )
        else:
            about_text = (
                "Это бот психологических тестов.\n\n"
                "Вы проходите три теста по цепочке:\n"
                "• Архетип личности\n"
                "• Код Тени\n"
                "• Внутреннее напряжение\n\n"
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

    if text == "Получить Код личности":
        context.user_data.clear()
        await update.message.reply_text(
            "Сначала завершите три базовых теста.",
            reply_markup=main_menu_markup,
        )
        return

    if text in BUTTON_TO_TEST_KEY:
        test_key = BUTTON_TO_TEST_KEY[text]
        context.user_data.clear()

        if has_full_access(results):
            await start_test(update, context, test_key, TESTS[test_key])
        else:
            await update.message.reply_text(
                "Сначала начните исследование. Порядок тестов: Архетип личности → Код Тени → Внутреннее напряжение.",
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
