import os
import time

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
from flows.paid_block.balance_wheel_flow import (
    start_balance_wheel,
    handle_balance_wheel_text,
    handle_balance_wheel_callback,
    _clear_state as clear_balance_wheel_state,
)
from flows.paid_block.deep_profile_flow import handle_paid_callback
from flows.paid_block.paid_access import has_paid_access
from flows.paid_block.payment_flow import (
    send_deep_profile_invoice,
    handle_pre_checkout,
    handle_successful_payment,
)
from flows.paid_block.paid_space_flow import (
    get_space_menu_keyboard,
    send_space_menu_text,
    send_about_space,
    send_tool_stub,
    is_space_tool_text,
)
from personality_code.upsell_screen import (
    get_payment_placeholder_text,
    get_full_profile_keyboard,
)
from tests.registry import TESTS
from storage.results_store import (
    get_user_results,
    delete_user_results,
    get_user_profile,
    reset_user_progress,
)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 5750354905
START_DEBOUNCE_SECONDS = 2.5
RECENT_STARTS = {}

if not TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")


START_KEYBOARD = ReplyKeyboardMarkup(
    [["Начать"]],
    resize_keyboard=True,
)

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
        menu.append(["Открыть пространство"])

    if is_admin(user_id):
        menu.append(["QA: открыть пространство"])
        menu.append(["Сбросить мои тесты"])

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
    return "Это система психологических тестов: быстрый вход и пространство для дальнейшей работы с собой."


def should_ignore_duplicate_start(user_id) -> bool:
    now = time.time()
    user_id = str(user_id)
    last = RECENT_STARTS.get(user_id, 0)
    RECENT_STARTS[user_id] = now
    return (now - last) < START_DEBOUNCE_SECONDS


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    context.user_data.clear()

    user = update.effective_user
    user_id = user.id if user else "unknown"

    clear_balance_wheel_state(user_id)

    if should_ignore_duplicate_start(user_id):
        return

    reset_user_progress(user_id)

    if has_paid_access(user_id):
        await update.message.reply_text(
            "Доступ к пространству уже открыт. Выбери, с чем хочешь поработать сегодня.",
            reply_markup=get_space_menu_keyboard(user_id),
        )
        return

    text = (
        "Привет. Меня зовут Наташа. Я психолог и работаю в интегративном подходе.\n\n"
        "Внутри тебя есть система, которая управляет твоими мыслями:\n\n"
        "1. что с тобой происходит и как ты реагируешь\n"
        "2. какие сценарии повторяешь\n"
        "3. где ты теряешь себя\n"
        "4. куда уходит энергия\n"
        "5. как это менять\n\n"
        "Я не работаю по одному методу.\n"
        "Я собрала систему, которая показывает человека целиком и помогает ему находить лучшие решения.\n\n"
        "Тебе не нужно больше искать ответы в разных местах. В этом приложении ты найдёшь всё, что поможет тебе каждый день справляться.\n\n"
        "Начнём с быстрого входа.\n\n"
        "Это займёт 2–3 минуты и покажет базовую картину."
    )

    await update.message.reply_text(
        text,
        reply_markup=START_KEYBOARD,
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()

    user = update.effective_user
    user_id = user.id if user else "unknown"
    results = get_user_results(user_id)
    main_menu_markup = get_main_menu(user_id)

    if text in {
        "Начать",
        "Начать исследование",
        "Мои результаты",
        "О тесте",
        "Открыть пространство",
        "ℹ️ О пространстве",
        "🔄 Назад",
        "QA: открыть пространство",
        "Сбросить мои тесты",
        "⚖️ Колесо баланса",
    } or is_space_tool_text(text):
        clear_balance_wheel_state(user_id)

    if text == "Открыть пространство":
        await send_space_menu_text(update, context)
        return

    if text == "ℹ️ О пространстве":
        await send_about_space(update, context)
        return

    if text == "🔄 Назад":
        await send_space_menu_text(update, context)
        return

    if text == "⚖️ Колесо баланса":
        await start_balance_wheel(update.message)
        return

    if is_space_tool_text(text):
        await send_tool_stub(update, context, text)
        return

    if text == "Сбросить мои тесты":
        if not is_admin(user_id):
            await update.message.reply_text(
                "Эта функция доступна только админу.",
                reply_markup=main_menu_markup,
            )
            return

        delete_user_results(user_id)
        context.user_data.clear()
        clear_balance_wheel_state(user_id)

        await update.message.reply_text(
            "Ваши результаты удалены.",
            reply_markup=get_main_menu(user_id),
        )
        return

    if text == "QA: открыть пространство":
        if not is_admin(user_id):
            await update.message.reply_text(
                "Эта функция доступна только админу.",
                reply_markup=main_menu_markup,
            )
            return

        clear_balance_wheel_state(user_id)

        await update.message.reply_text(
            "Доступ к пространству открыт.",
            reply_markup=get_space_menu_keyboard(user_id),
        )
        return

    if text == "Начать":
        reset_user_progress(user_id)
        context.user_data.clear()
        clear_balance_wheel_state(user_id)
        await send_entry_screen(update, context, get_main_menu(user_id))
        return

    if text == "Начать исследование":
        reset_user_progress(user_id)
        context.user_data.clear()
        clear_balance_wheel_state(user_id)
        await send_entry_screen(update, context, get_main_menu(user_id))
        return

    if text == "Мои результаты":
        context.user_data.clear()
        clear_balance_wheel_state(user_id)

        await update.message.reply_text(
            build_results_text(results),
            reply_markup=get_main_menu(user_id),
            parse_mode="Markdown",
        )

        profile = get_user_profile(user_id)
        if profile.get("deep_profile_result"):
            await update.message.reply_text(
                profile["deep_profile_result"],
                reply_markup=get_main_menu(user_id),
            )
        return

    if text == "О тесте":
        context.user_data.clear()
        clear_balance_wheel_state(user_id)

        await update.message.reply_text(
            build_about_text(),
            reply_markup=get_main_menu(user_id),
        )
        return

    handled_by_balance = await handle_balance_wheel_text(update, context)
    if handled_by_balance:
        return

    await update.message.reply_text(
        "Используйте кнопки ниже.",
        reply_markup=get_main_menu(user_id),
    )


async def handle_all_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        return

    await query.answer()
    data = query.data

    user = update.effective_user
    user_id = user.id if user else "unknown"

    handled_by_balance = await handle_balance_wheel_callback(update, context)
    if handled_by_balance:
        return

    if data == "learn_more":
        await update.effective_chat.send_message(
            get_payment_placeholder_text(),
            reply_markup=get_full_profile_keyboard(),
        )
        return

    if data in ("full_profile_info", "buy_full_code"):
        if is_admin(user_id):
            await update.effective_chat.send_message(
                "QA доступ включён.",
                reply_markup=get_space_menu_keyboard(user_id),
            )
            return

        if has_paid_access(user_id):
            await update.effective_chat.send_message(
                "Доступ уже открыт.",
                reply_markup=get_space_menu_keyboard(user_id),
            )
        else:
            await send_deep_profile_invoice(update, context)
        return

    if data in ("open_space",):
        await handle_paid_callback(update, context)
        return

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
