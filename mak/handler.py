from telegram import InputFile
from mak.cards_loader import load_cards, get_random_card
from mak.texts import DECK_TEXTS

decks_cache = None


def get_decks():
    global decks_cache
    if decks_cache is None:
        decks_cache = load_cards()
    return decks_cache


async def send_random_card(update, context, deck_name=None):
    decks = get_decks()

    deck, card_path = get_random_card(decks, deck_name)

    if not card_path:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Карты пока не загружены",
        )
        return

    text_data = DECK_TEXTS.get(deck, {})
    title = text_data.get("title", "Карта")
    description = text_data.get("description", "")

    caption = f"*{title}*\n\n{description}"

    with open(card_path, "rb") as photo:
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=InputFile(photo),
            caption=caption,
            parse_mode="Markdown",
        )
