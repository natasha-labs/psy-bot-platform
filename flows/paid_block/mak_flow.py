import os
import random
from datetime import datetime

from telegram import InlineKeyboardMarkup, InlineKeyboardButton, InputFile

from mak.cards_loader import load_cards
from mak.texts import DECK_TEXTS

try:
    from storage.results_store import load_results, save_results
except Exception:
    load_results = None
    save_results = None

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


def _pick_random_card():
    decks = get_decks()

    valid_decks = []
    for deck, images in decks.items():
        if not images:
            continue
        if deck not in DECK_TEXTS:
            continue
        if not DECK_TEXTS[deck].get("meaning"):
            continue
        if not DECK_TEXTS[deck].get("questions"):
            continue
        valid_decks.append(deck)

    if not valid_decks:
        return None

    deck = random.choice(valid_decks)
    image_path = random.choice(decks[deck])
    question = random.choice(DECK_TEXTS[deck]["questions"])

    return {
        "deck": deck,
        "image_path": image_path,
        "meaning": DECK_TEXTS[deck]["meaning"],
        "question": question,
        "image_filename": os.path.basename(image_path),
    }


def _save_mak_history(user_id, card_data):
    if load_results is None or save_results is None:
        return

    try:
        data = load_results()
        uid = str(user_id)

        if uid not in data:
            data[uid] = {
                "user_id": user_id,
                "completed_tests": [],
                "results": {},
                "paid_access": False,
            }

        if "results" not in data[uid]:
            data[uid]["results"] = {}

        if "mak_history" not in data[uid]["results"]:
            data[uid]["results"]["mak_history"] = []

        data[uid]["results"]["mak_history"].append(
            {
                "timestamp": datetime.utcnow().isoformat(),
                "theme": card_data["deck"],
                "image_filename": card_data["image_filename"],
                "question": card_data["question"],
            }
        )

        save_results(data)
    except Exception:
        pass


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


async def _send_mak_card(update, context):
    chat_id = update.effective_chat.id
    user = update.effective_user
    user_id = user.id if user else "unknown"

    card_data = _pick_random_card()

    if not card_data:
        await context.bot.send_message(
            chat_id=chat_id,
            text="Сейчас карты временно недоступны. Попробуй позже.",
        )
        return

    _save_mak_history(user_id, card_data)

    caption = (
        f"{card_data['meaning']}\n\n"
        f"*Вопрос для тебя:*\n"
        f"{card_data['question']}"
    )

    with open(card_data["image_path"], "rb") as photo:
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=InputFile(photo),
            caption=caption,
            parse_mode="Markdown",
            reply_markup=get_mak_result_keyboard(),
        )


async def handle_mak_callback(update, context):
    query = update.callback_query
    if not query:
        return False

    data = query.data or ""

    if data == "mak_draw":
        try:
            await query.edit_message_reply_markup(reply_markup=None)
        except Exception:
            pass

        await _send_mak_card(update, context)
        return True

    if data == "mak_finish":
        try:
            await query.edit_message_reply_markup(reply_markup=None)
        except Exception:
            pass
        return True

    return False
