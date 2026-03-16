from tests.archetype.test_def import TEST_DEF
from engine.test_engine import start_test, handle_nav_text


async def start_archetype_test(update, context):
    await start_test(update, context, "archetype", TEST_DEF)


async def handle_archetype_answer(update, context, main_menu_markup):
    await handle_nav_text(
        update,
        context,
        main_menu_markup,
        {"archetype": TEST_DEF},
    )
