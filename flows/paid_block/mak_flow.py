import random
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, InputFile

from mak.cards_loader import load_cards

decks_cache = None


def get_decks():
    global decks_cache
    if decks_cache is None:
        decks_cache = load_cards()
    return decks_cache


def reset_state(context):
    context.user_data["mak"] = {
        "card": None,
    }


def get_state(context):
    return context.user_data.get("mak", {})


def start_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Открыть карту", callback_data="mak_draw")]
    ])


def next_from_card_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Дальше", callback_data="mak_step_contact")]
    ])


def next_from_contact_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Дальше", callback_data="mak_step_life")]
    ])


def final_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Ещё карта", callback_data="mak_draw")],
        [InlineKeyboardButton("Назад в пространство", callback_data="mak_finish")],
    ])


def pick_card():
    decks = get_decks()
    valid = [deck for deck in decks if decks[deck]]

    if not valid:
        return None

    deck = random.choice(valid)
    return random.choice(decks[deck])


async def send_mak_entry(update, context):
    reset_state(context)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            "Ты смотришь не на карту.\n"
            "Ты смотришь на себя через неё.\n\n"
            "В этом нет правильного ответа.\n"
            "Нет значения, которое нужно найти.\n\n"
            "Есть только то, что появляется у тебя внутри.\n\n"
            "Это может быть чувство, мысль, образ\n"
            "или вообще ничего.\n\n"
            "Не нужно это менять или объяснять.\n"
            "Просто позволь этому быть."
        ),
        reply_markup=start_keyboard(),
    )


async def send_card(update, context):
    image = pick_card()

    if not image:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Карты временно недоступны",
        )
        return

    context.user_data["mak"]["card"] = image

    with open(image, "rb") as photo:
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=InputFile(photo),
            caption=(
                "Посмотри на изображение.\n\n"
                "Не спеши. Просто побудь с ним несколько секунд.\n\n"
                "━━━━━━━━━━━━━━\n\n"
                "Обрати внимание, что притягивает взгляд.\n\n"
                "И что происходит внутри, когда ты на это смотришь.\n\n"
                "Не нужно называть это правильно. Можно просто заметить.\n\n"
                "Если ничего не происходит — это тоже нормально.\n\n"
                "━━━━━━━━━━━━━━\n\n"
                "Если хочется, посмотри — есть ли в твоей жизни что-то с похожим ощущением.\n\n"
                "Можно задать себе вопрос к этому образу. Или ничего не задавать.\n\n"
                "Иногда достаточно просто побыть с этим.\n\n"
                "━━━━━━━━━━━━━━\n\n"
                "Обрати внимание, с чем ты сейчас остаёшься.\n\n"
                "Это может быть мысль, ощущение, образ или просто состояние.\n\n"
                "Этого достаточно."
            ),
            reply_markup=next_from_card_keyboard(),
        )


async def send_contact_step(update, context):
    return True


async def send_life_step(update, context):
    return True


async def handle_mak_callback(update, context):
    query = update.callback_query
    if not query:
        return False

    data = query.data or ""

    if not data.startswith("mak_"):
        return False

    try:
        await query.edit_message_reply_markup(None)
    except Exception:
        pass

    if data == "mak_draw":
        reset_state(context)
        await send_card(update, context)
        return True

    if data == "mak_step_contact":
        await send_contact_step(update, context)
        return True

    if data == "mak_step_life":
        await send_life_step(update, context)
        return True

    if data == "mak_finish":
        from flows.paid_block.paid_space_flow import send_space_menu_text
        await send_space_menu_text(update, context)
        return True

    return False
