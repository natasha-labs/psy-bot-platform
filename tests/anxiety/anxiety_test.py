from tests.anxiety.test_def import TEST_DEF
from engine.test_engine import start_test, handle_nav_text


async def start_anxiety_test(update, context):
    await start_test(update, context, "anxiety", TEST_DEF)


async def handle_anxiety_answer(update, context, main_menu_markup):
    await handle_nav_text(
        update,
        context,
        main_menu_markup,
        {"anxiety": TEST_DEF},
    )


async def handle_anxiety_nav(action, update, context, main_menu_markup):
    if action == "main_menu" or action == "to_tests":
        context.user_data.clear()
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Выберите тест:",
            reply_markup=main_menu_markup,
        )
        return

    await handle_anxiety_answer(update, context, main_menu_markup)
