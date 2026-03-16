from tests.shadow.test_def import TEST_DEF
from engine.test_engine import start_test, handle_nav_text


async def start_shadow_test(update, context):
    await start_test(update, context, "shadow", TEST_DEF)


async def handle_shadow_answer(update, context, main_menu_markup):
    await handle_nav_text(
        update,
        context,
        main_menu_markup,
        {"shadow": TEST_DEF},
    )
