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
