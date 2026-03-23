import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    PreCheckoutQueryHandler,
    filters,
)

from engine.test_engine import send_entry_screen, handle_callback as handle_free_callback
from flows.paid_block.paid_entry import send_paid_entry
from flows.paid_block.deep_profile_flow import handle_paid_callback
from flows.paid_block.paid_access import has_paid_access
from flows.paid_block.payment_flow import (
    send_deep_profile_invoice,
    handle_pre_checkout,
    handle_successful_payment,
)
from tests.registry import TESTS
from storage.results_store import (
    get_user_results,
    delete_user_results,
    get_user_profile,
    set_paid_access,
)

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

    if has_paid_access(user_id):
        menu.append(["Открыть платный блок"])

    if is_admin(user_id):
        menu.append(["QA: открыть блок 2"])
        menu.append(["Сбросить мои тесты"])
        menu.append(["Выдать платный доступ"])
        menu.append(["Забрать платный доступ"])

    return ReplyKeyboardMarkup(menu, resize_keyboard=True)


def build_results_text(results: dict) -> str:
    if not results:
        return "У вас пока нет сохранённых результатов."

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
    return "Это система психологических тестов: бесплатный блок и платный глубокий разбор."


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
            reply_markup=get_main_menu(user_id),
        )
        return

    if text == "Выдать платный доступ":
        if is_admin(user_id):
            set_paid_access(user_id, True)
            await update.message.reply_text(
                "Платный доступ выдан.",
                reply_markup=get_main_menu(user_id),
            )
        return

    if text == "Забрать платный доступ":
        if is_admin(user_id):
            set_paid_access(user_id, False)
            await update.message.reply_text(
                "Платный доступ снят.",
                reply_markup=get_main_menu(user_id),
            )
        return

    if text == "QA: открыть блок 2":
        if not is_admin(user_id):
            await update.message.reply_text(
                "Эта функция доступна только админу.",
                reply_markup=main_menu_markup,
            )
            return

        set_paid_access(user_id, True)
        await send_paid_entry(update, context)
        return

    if text == "Начать исследование":
        context.user_data.clear()
        await send_entry_screen(update, context, main_menu_markup)
        return

    if text == "Открыть платный блок":
        if has_paid_access(user_id):
            await send_paid_entry(update, context)
        else:
            await send_deep_profile_invoice(update, context)
        return

    if text == "Мои результаты":
        context.user_data.clear()
        await update.message.reply_text(
            build_results_text(results),
            reply_markup=main_menu_markup,
            parse_mode="Markdown",
        )

        profile = get_user_profile(user_id)
        if profile.get("deep_profile_result"):
            await update.message.reply_text(
                profile["deep_profile_result"],
                reply_markup=main_menu_markup,
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
    query = update.callback_query
    if not query:
        return

    await query.answer()
    data = query.data

    user = update.effective_user
    user_id = user.id if user else "unknown"

    # Кнопка с финала бесплатного блока
    if data in ("full_profile_info", "buy_full_code"):
        if has_paid_access(user_id):
            await send_paid_entry(update, context)
        else:
            await send_deep_profile_invoice(update, context)
        return

    # Весь платный блок
    if data.startswith("paid_") or data == "start_deep_profile":
        await handle_paid_callback(update, context)
        return

    # Всё остальное — бесплатный блок
    main_menu_markup = get_main_menu(user_id)
    await handle_free_callback(update, context, main_menu_markup, TESTS)


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_all_callbacks))
    app.add_handler(PreCheckoutQueryHandler(handle_pre_checkout))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, handle_successful_payment))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()


if __name__ == "__main__":
    main()
