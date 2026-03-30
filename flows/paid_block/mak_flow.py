import os
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


# ---------- KEYBOARDS ----------

def start_keyboard():
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("Вытянуть первую карту", callback_data="mak_1")]]
    )


def reveal_keyboard(step):
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("Получить значение карты", callback_data=f"mak_reveal_{step}")]]
    )


def next_keyboard(step):
    if step == 1:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("Вытянуть вторую карту", callback_data="mak_2")],
            [InlineKeyboardButton("Завершить", callback_data="mak_finish")]
        ])
    if step == 2:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("Вытянуть третью карту", callback_data="mak_3")],
            [InlineKeyboardButton("Завершить", callback_data="mak_finish")]
        ])


def final_keyboard():
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("Сделать новый расклад", callback_data="mak_restart")]]
    )


# ---------- LOGIC ----------

def pick_card():
    decks = get_decks()

    valid = [d for d in decks if d in DECK_TEXTS and decks[d]]
    if not valid:
        return None

    deck = random.choice(valid)
    image = random.choice(decks[deck])

    return {
        "deck": deck,
        "image": image,
        "meaning": DECK_TEXTS[deck]["meaning"],
        "question": random.choice(DECK_TEXTS[deck]["questions"])
    }


# ---------- ENTRY ----------

async def send_mak_entry(update, context):
    context.user_data["mak_step"] = 0
    context.user_data["mak_cards"] = []

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            "*Метафорические карты*\n\n"
            "Иногда одна карта попадает точнее, чем длинный разговор.\n"
            "Подумай сейчас о том что тебя больше всего волнует\n"
            "Вытяни 3 карты и посмотри, что они откроют тебе."
        ),
        parse_mode="Markdown",
        reply_markup=start_keyboard(),
    )


# ---------- SEND CARD ----------

async def send_card(update, context, step):
    card = pick_card()

    if not card:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Карты временно недоступны",
        )
        return

    context.user_data["mak_cards"].append(card)
    context.user_data["mak_step"] = step

    with open(card["image"], "rb") as photo:
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=InputFile(photo),
            caption="Посмотри внимательно на карту.\nЧто ты чувствуешь?",
            reply_markup=reveal_keyboard(step),
        )


# ---------- REVEAL ----------

async def reveal_card(update, context, step):
    card = context.user_data["mak_cards"][step - 1]

    text = (
        f"{card['meaning']}\n\n"
        f"*Вопрос:*\n{card['question']}"
    )

    if step == 3:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=(
                f"{text}\n\n"
                "Это был твой расклад на ситуацию.\n\n"
                "Не спеши искать правильный ответ.\n"
                "Сначала просто посмотри, что внутри отзывается."
            ),
            parse_mode="Markdown",
            reply_markup=final_keyboard(),
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            parse_mode="Markdown",
            reply_markup=next_keyboard(step),
        )


# ---------- CALLBACK ----------

async def handle_mak_callback(update, context):
    query = update.callback_query
    data = query.data

    try:
        await query.edit_message_reply_markup(None)
    except:
        pass

    if data == "mak_restart":
        await send_mak_entry(update, context)
        return True

    if data == "mak_finish":
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Ты можешь вернуться к этому позже.",
        )
        return True

    if data == "mak_1":
        await send_card(update, context, 1)
        return True

    if data == "mak_2":
        await send_card(update, context, 2)
        return True

    if data == "mak_3":
        await send_card(update, context, 3)
        return True

    if data.startswith("mak_reveal_"):
        step = int(data.split("_")[-1])
        await reveal_card(update, context, step)
        return True

    return False
