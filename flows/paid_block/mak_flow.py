import random
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, InputFile

from mak.cards_loader import load_cards

decks_cache = None


def get_decks():
    global decks_cache
    if decks_cache is None:
        decks_cache = load_cards()
    return decks_cache


# ================== STATE ==================

def reset_state(context):
    context.user_data["mak"] = {
        "step": "start",
        "card": None,
        "type": None,
        "base": None,
        "sub": None,
        "life": None,
    }


def get_state(context):
    return context.user_data.get("mak", {})


# ================== KEYBOARDS ==================

def start_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Вытянуть карту", callback_data="mak_draw")]
    ])


def type_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Чувство", callback_data="mak_type_feeling")],
        [InlineKeyboardButton("Мысль", callback_data="mak_type_thought")],
        [InlineKeyboardButton("Образ", callback_data="mak_type_image")],
        [InlineKeyboardButton("Воспоминание", callback_data="mak_type_memory")],
    ])


def feeling_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Напряжение", callback_data="mak_base_tension")],
        [InlineKeyboardButton("Спокойствие", callback_data="mak_base_calm")],
        [InlineKeyboardButton("Тепло", callback_data="mak_base_warm")],
        [InlineKeyboardButton("Тяжесть", callback_data="mak_base_heavy")],
        [InlineKeyboardButton("Пустота", callback_data="mak_base_empty")],
    ])


def sub_keyboard(base):
    mapping = {
        "tension": ["Тревога", "Раздражение", "Страх", "Давление", "Беспокойство"],
        "warm": ["Любовь", "Радость", "Нежность", "Уют", "Благодарность"],
        "heavy": ["Усталость", "Грусть", "Апатия", "Перегруз", "Опустошение"],
        "calm": ["Равновесие", "Принятие", "Уверенность", "Расслабленность", "Отпускание"],
        "empty": ["Отстранённость", "Потерянность", "Отключённость", "Безразличие", "Зависание"],
    }

    return InlineKeyboardMarkup([
        [InlineKeyboardButton(x, callback_data=f"mak_sub_{x}")]
        for x in mapping.get(base, [])
    ])


def life_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Я сам", callback_data="mak_life_self")],
        [InlineKeyboardButton("Отношения", callback_data="mak_life_rel")],
        [InlineKeyboardButton("Моё состояние", callback_data="mak_life_state")],
        [InlineKeyboardButton("Выбор / решение", callback_data="mak_life_choice")],
        [InlineKeyboardButton("Не понимаю", callback_data="mak_life_none")],
    ])


def final_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Вытянуть ещё карту", callback_data="mak_draw")],
        [InlineKeyboardButton("Завершить", callback_data="mak_finish")],
    ])


# ================== CARD ==================

def pick_card():
    decks = get_decks()
    valid = [d for d in decks if decks[d]]

    if not valid:
        return None

    deck = random.choice(valid)
    return random.choice(decks[deck])


# ================== OUTPUT ==================

OUTPUTS = {
    "tension": [
        "Похоже, сейчас внутри есть напряжение\n\nОбычно оно появляется там, где есть контроль\n\nИногда достаточно просто это заметить"
    ],
    "warm": [
        "Здесь есть тепло\n\nЭто состояние контакта\n\nЕго не нужно усиливать"
    ],
    "calm": [
        "Здесь есть спокойствие\n\nЭто внутренняя устойчивость\n\nМожно не спешить"
    ],
    "heavy": [
        "В этом есть тяжесть\n\nВозможно, накопилось слишком много\n\nСейчас важно не добавлять"
    ],
    "empty": [
        "В этом есть пустота\n\nИногда это пауза, а не проблема\n\nЭто тоже часть процесса"
    ],
}


# ================== FLOW ==================

async def send_mak_entry(update, context):
    reset_state(context)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            "*Метафорические карты — это не тест и не гадание*\n"
            "У них нет правильного значения\n"
            "Одна и та же карта может вызывать у разных людей совершенно разные чувства и ассоциации\n"
            "Здесь важно не то, что “изображено”, а то, что откликается именно у тебя\n\n"
            "Когда ты смотришь на карту, обрати внимание:\n"
            "— что ты чувствуешь\n"
            "— какие мысли приходят\n"
            "— какие образы или воспоминания возникают\n\n"
            "Не нужно искать правильный ответ или пытаться понять “как надо”\n"    
            "Выбери то, что откликнулось у тебя первым\n"
            "Именно с этим мы и будем работать дальше"
        ),
        parse_mode="Markdown",
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
            caption="Посмотри внимательно\n\nЧто откликнулось первым?",
            reply_markup=type_keyboard(),
        )


# ================== CALLBACK ==================

async def handle_mak_callback(update, context):
    query = update.callback_query
    data = query.data

    try:
        await query.edit_message_reply_markup(None)
    except:
        pass

    state = get_state(context)

    # старт
    if data == "mak_draw":
        await send_card(update, context)
        return True

    # тип
    if data.startswith("mak_type_"):
        state["type"] = data.split("_")[-1]

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Что это за состояние?",
            reply_markup=feeling_keyboard(),
        )
        return True

    # база
    if data.startswith("mak_base_"):
        base = data.split("_")[-1]
        state["base"] = base

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Уточни",
            reply_markup=sub_keyboard(base),
        )
        return True

    # уточнение
    if data.startswith("mak_sub_"):
        state["sub"] = data.replace("mak_sub_", "")

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Где это есть в твоей жизни?",
            reply_markup=life_keyboard(),
        )
        return True

    # жизнь
    if data.startswith("mak_life_"):
        state["life"] = data

        base = state.get("base")
        text = random.choice(OUTPUTS.get(base, ["Просто заметь это состояние"]))

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            reply_markup=final_keyboard(),
        )
        return True

    # завершить
    if data == "mak_finish":
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Ты можешь вернуться к этому позже",
        )
        return True

    return False
