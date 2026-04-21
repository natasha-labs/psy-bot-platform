import random
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from tests.karpman.questions import questions


def reset_state(context):
    shuffled = questions[:]
    random.shuffle(shuffled)

    context.user_data["karpman"] = {
        "questions": shuffled,
        "index": 0,
        "victim_score": 0,
        "rescuer_score": 0,
        "persecutor_score": 0,
    }


def get_state(context):
    return context.user_data.get("karpman")


def start_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Начать тест", callback_data="karpman_start")]
    ])


def answer_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Полностью согласен", callback_data="karpman_answer:4")],
        [InlineKeyboardButton("В некоторой степени согласен", callback_data="karpman_answer:3")],
        [InlineKeyboardButton("Затрудняюсь ответить", callback_data="karpman_answer:2")],
        [InlineKeyboardButton("В некоторой степени не согласен", callback_data="karpman_answer:1")],
        [InlineKeyboardButton("Категорически не согласен", callback_data="karpman_answer:0")],
    ])


async def send_karpman_entry(update, context):
    reset_state(context)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            "Американский психотерапевт, доктор медицины и ученик Эрика Берна, Стивен Карпман в 1968 году "
            "описал психолого-социальную модель взаимодействия между людьми. Изначально свою схему он назвал "
            "«Драматический треугольник», но после за ней закрепилось его имя.\n\n"
            "Треугольник Карпмана представляет собой модель конфликтного общения, на основе которого формируются "
            "созависимые отношения. В данной модели выделяется три роли: жертва, спасатель, преследователь.\n\n"
            "У каждой позиции в конфликтной ситуации имеются свои выгоды:\n"
            "Жертва перекладывает ответственность на других людей.\n"
            "Спасатель начинает чувствовать свою значимость за счет помощи другим.\n"
            "Преследователь стабилизирует свою самооценку за счет позиции силы.\n\n"
            "Треугольник Карпмана применим для работы в коллективе, школе, семейных отношениях.\n"
            "Желаете узнать, какую позицию вы принимаете чаще всего в конфликтных ситуациях? Тогда жмите кнопку «начать»!"
        ),
        reply_markup=start_keyboard(),
    )


async def send_question(chat_id, context):
    state = get_state(context)
    if not state:
        return

    question = state["questions"][state["index"]]
    total = len(state["questions"])
    current = state["index"] + 1

    await context.bot.send_message(
        chat_id=chat_id,
        text=f"Вопрос {current} из {total}\n\n{question['text']}",
        reply_markup=answer_keyboard(),
    )


def calculate_percents(state):
    max_score = 8 * 4

    victim_percent = round(state["victim_score"] / max_score * 100)
    rescuer_percent = round(state["rescuer_score"] / max_score * 100)
    persecutor_percent = round(state["persecutor_score"] / max_score * 100)

    return {
        "victim": victim_percent,
        "rescuer": rescuer_percent,
        "persecutor": persecutor_percent,
    }


def detect_main_type(percents):
    sorted_roles = sorted(percents.items(), key=lambda item: item[1], reverse=True)
    main_role, main_value = sorted_roles[0]
    second_role, second_value = sorted_roles[1]

    mixed = abs(main_value - second_value) < 10
    return main_role, mixed


def build_result_text(percents):
    main_role, mixed = detect_main_type(percents)

    victim = percents["victim"]
    rescuer = percents["rescuer"]
    persecutor = percents["persecutor"]

    if mixed:
        header = "Твоя ведущая позиция — Смешанный тип\n\n"
        body = (
            "У тебя нет одной фиксированной роли.\n"
            "Ты переключаешься между позициями в зависимости от ситуации.\n"
            "Это даёт гибкость, но может создавать ощущение нестабильности.\n"
            "Что важно:\n"
            "наблюдать, какая роль включается чаще всего и в какие моменты."
        )
    elif main_role == "persecutor":
        header = f"Твоя ведущая позиция — Преследователь ({persecutor}%)\n\n"
        body = (
            f"Позиция преследователь — {persecutor}%.\n"
            "Человек, играющий данную роль, чувствует свое превосходство над другими людьми. "
            "Преследователи прячут свою истинную сущность под маской лжи. Они всегда готовы осудить "
            "или раскритиковать, следуют закону джунглей (лучшая защита – это нападение). Их слова "
            "расходятся с действиями, презирают слабость.\n"
            "Как это можно изменить?\n"
            "Перестать обижаться на весь мир, стараться видеть в других людях положительные качества "
            "(вместо недостатков). Начните строить с людьми партнерские отношения (вместо зависимых), "
            "откажитесь от неконструктивной критики и осуждений."
        )
    elif main_role == "victim":
        header = f"Твоя ведущая позиция — Жертва ({victim}%)\n\n"
        body = (
            f"Позиция жертвы — {victim}%.\n"
            "К чертам характера такого человека относится беспомощность, неумение самостоятельно "
            "решать проблемные ситуации, избегание ответственности, пассивность. Он считает, что жизнь – "
            "это страдание, а люди к нему не справедливы. И чаще всего именно другие виноваты в его бедах. "
            "Из данной роли очень сложно выйти, так как в ней наблюдается много плюсов: постоянная поддержка, "
            "внимание, жалость со стороны других людей. Снятие высоких требований, ожиданий.\n"
            "Для изменения данной позиции необходимо: перестать ставить себя ниже других, начать рассчитывать "
            "на свои силы, перестать советоваться с другими людьми и жаловаться на жизнь."
        )
    else:
        header = f"Твоя ведущая позиция — Спасатель ({rescuer}%)\n\n"
        body = (
            f"Позиция спасатель — {rescuer}%.\n"
            "Люди с такой позицией уверены, что без их помощи никто не сможет ничего сделать. Спасатели ощущают "
            "себя исключительными, единственными. В их голове часто проскакивают подобные мысли: «Только я могу "
            "ей/ему помочь», «Только на мне держится эта семья», «Без меня проект обречен на провал». В результате "
            "такие люди сталкиваются с неблагодарностью или, еще хуже, оказываются виноватыми во всех бедах.\n"
            "Чтобы выйти из позиции спасателя, то вам в первую очередь следует: обратить свой фокус внимание на себя "
            "(свои проблемы, потребности, дела), перестать давать непрошенные советы и стремиться решать за кого-то "
            "проблемы, начать отказывать людям."
        )

    footer = (
        f"\n\nЖертва — {victim}%\n"
        f"Спасатель — {rescuer}%\n"
        f"Преследователь — {persecutor}%\n\n"
        "Результаты, полученные без участия специалиста, не воспринимайте слишком серьезно.\n\n"
        "Выбери следующую практику в меню ниже."
    )

    return header + body + footer


async def handle_karpman_callback(update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        return False

    data = query.data or ""
    if not data.startswith("karpman_"):
        return False

    try:
        await query.edit_message_reply_markup(reply_markup=None)
    except Exception:
        pass

    chat_id = update.effective_chat.id

    if data == "karpman_start":
        await send_question(chat_id, context)
        return True

    if data.startswith("karpman_answer:"):
        state = get_state(context)
        if not state:
            return True

        value = int(data.split(":")[1])
        current_question = state["questions"][state["index"]]
        role = current_question["role"]

        if role == "victim":
            state["victim_score"] += value
        elif role == "rescuer":
            state["rescuer_score"] += value
        elif role == "persecutor":
            state["persecutor_score"] += value

        state["index"] += 1

        if state["index"] >= len(state["questions"]):
            percents = calculate_percents(state)
            result_text = build_result_text(percents)
            await context.bot.send_message(chat_id=chat_id, text=result_text)
            context.user_data.pop("karpman", None)
            return True

        await send_question(chat_id, context)
        return True

    return False
