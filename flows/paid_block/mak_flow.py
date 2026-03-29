import random
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, InputFile

from mak.cards_loader import load_cards
from mak.texts import DECK_TEXTS

decks_cache = None


def get_decks():
    global decks_cache
    if decks_cache is None:
        decks_cache = load_cards()
    return decks_cache


def get_mak_entry_keyboard():
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("Вытянуть карту", callback_data="mak_draw")]]
    )


def get_mak_result_keyboard():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Ещё карта", callback_data="mak_draw")],
            [InlineKeyboardButton("Завершить", callback_data="mak_finish")],
        ]
    )


async def send_mak_entry(update, context):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            "*Метафорические карты*\n\n"
            "Иногда одна карта попадает точнее, чем длинный разговор.\n"
            "Вытяни карту и посмотри, что она откроет тебе сейчас."
        ),
        parse_mode="Markdown",
        reply_markup=get_mak_entry_keyboard(),
    )


def pick_random_card(decks):
    valid_decks = []

    for deck, images in decks.items():
        if not images:
            continue
        if deck not in DECK_TEXTS:
            continue
        valid_decks.append(deck)

    if not valid_decks:
        return None, None

    deck = random.choice(valid_decks)
    image = random.choice(decks[deck])

    return deck, image


async def send_mak_card(update, context):
    decks = get_decks()

    deck, image_path = pick_random_card(decks)

    if not image_path:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Сейчас карты временно недоступны. Попробуй позже.",
        )
        return

    text_data = DECK_TEXTS.get(deck, {})
    meaning = text_data.get("meaning", "")
    questions = text_data.get("questions", [])

    question = random.choice(questions) if questions else ""

    caption = f"{meaning}\n\n*Вопрос для тебя:*\n{question}"

    with open(image_path, "rb") as photo:
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=InputFile(photo),
            caption=caption,
            parse_mode="Markdown",
            reply_markup=get_mak_result_keyboard(),
        )


async def handle_mak_callback(update, context):
    query = update.callback_query
    data = query.data

    if data == "mak_draw":
        try:
            await query.edit_message_reply_markup(reply_markup=None)
        except Exception:
            pass

        await send_mak_card(update, context)
        return True

    if data == "mak_finish":
        try:
            await query.edit_message_reply_markup(reply_markup=None)
        except Exception:
            pass

        return True

    return False
