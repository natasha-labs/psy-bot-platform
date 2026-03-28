import os
from typing import Dict, Any

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from tests.balance_wheel.questions import SPHERES
from tests.balance_wheel.visual import generate_wheel

BALANCE_WHEEL_STATE: Dict[str, Dict[str, Any]] = {}

SPHERE_HINTS = {
    "Здоровье": "тонус, самочувствие, энергия, профилактика",
    "Деньги": "доход, стабильность, лёгкость заработка",
    "Отдых": "путешествия, развлечения, восстановление, встречи",
    "Окружение": "круг общения, поддержка, статус",
    "Обучение": "развитие, знания, учителя, книги",
    "Творчество": "хобби, самовыражение, любимое дело, вдохновение",
    "Работа и реализация": "успех, рост, влияние, интересные проекты",
    "Отношения": "любовь, близость, доверие, друзья",
    "Развитие": "осознанность, мышление, внутренний рост",
}

QUESTIONS = [
    {
        "type": "choice",
        "key": "satisfaction",
        "question": "Насколько ты сейчас доволен этой сферой?",
        "options": ["Очень плохо", "Плохо", "Средне", "Хорошо", "Очень хорошо"],
        "scores": [1, 2, 3, 4, 5],
    },
    {
        "type": "choice",
        "key": "importance",
        "question": "Насколько это важно для тебя?",
        "options": ["Не важно", "Скорее не важно", "Средне", "Важно", "Очень важно"],
        "scores": [1, 2, 3, 4, 5],
    },
    {
        "type": "choice",
        "key": "action",
        "question": "Что ты сейчас делаешь для развития этой сферы?",
        "options": ["Я этим занимаюсь", "Иногда уделяю внимание", "Пока откладываю"],
        "scores": [3, 2, 1],
    },
    {
        "type": "text",
        "key": "meaning",
        "question": "Напиши несколько слов, что в этой сфере жизни для вас важно.",
    },
]


def _user_key(user_id) -> str:
    return str(user_id)


def _get_state(user_id):
    return BALANCE_WHEEL_STATE.get(_user_key(user_id))


def _set_state(user_id, state: dict):
    BALANCE_WHEEL_STATE[_user_key(user_id)] = state


def _clear_state(user_id):
    BALANCE_WHEEL_STATE.pop(_user_key(user_id), None)


def _is_finished(state: dict) -> bool:
    return state["sphere_index"] >= len(SPHERES)


def _current_sphere(state: dict):
    if _is_finished(state):
        return None
    return SPHERES[state["sphere_index"]]


def _current_question(state: dict):
    if _is_finished(state):
        return None
    idx = state["question_index"]
    if idx < 0 or idx >= len(QUESTIONS):
        return None
    return QUESTIONS[idx]


def _build_choice_keyboard(options):
    rows = []
    for idx, option in enumerate(options):
        rows.append([InlineKeyboardButton(option, callback_data=f"bw_choice:{idx}")])
    return InlineKeyboardMarkup(rows)


def _build_find_resource_keyboard():
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("Найти ресурс", callback_data="bw_find_resource")]]
    )


def _build_resource_keyboard():
    rows = []
    for idx, sphere in enumerate(SPHERES):
        rows.append([InlineKeyboardButton(sphere, callback_data=f"bw_resource:{idx}")])
    return InlineKeyboardMarkup(rows)


def _advance(state: dict):
    state["question_index"] += 1
    if state["question_index"] >= len(QUESTIONS):
        state["question_index"] = 0
        state["sphere_index"] += 1


def _append_history(state: dict, question_text: str, answer_text: str):
    sphere = _current_sphere(state)
    if sphere is None:
        return

    history = state["answers"].setdefault(
        sphere,
        {
            "summary_lines": [f"Сфера {state['sphere_index'] + 1} из {len(SPHERES)}: {sphere}", ""],
            "satisfaction": 1,
            "importance": 1,
            "action": 1,
            "meaning": "",
        },
    )

    history["summary_lines"].append(question_text)
    history["summary_lines"].append(f"Ответ: {answer_text}")
    history["summary_lines"].append("")


def _get_sphere_summary(state: dict, sphere: str) -> str:
    info = state["answers"].get(sphere, {})
    lines = info.get("summary_lines", [])
    return "\n".join(lines).strip()


async def _send_current_step(chat_id: int, user_id, bot):
    state = _get_state(user_id)
    if not state:
        return

    if _is_finished(state):
        await _finish_wheel(chat_id, user_id, bot)
        return

    sphere = _current_sphere(state)
    question = _current_question(state)
    if sphere is None or question is None:
        await _finish_wheel(chat_id, user_id, bot)
        return

    summary = _get_sphere_summary(state, sphere)
    header = f"Сфера {state['sphere_index'] + 1} из {len(SPHERES)}: {sphere}"

    if not summary:
        base_text = header
    else:
        base_text = summary

    if question["type"] == "choice":
        text = f"{base_text}\n\n{question['question']}"
        await bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=_build_choice_keyboard(question["options"]),
        )
        return

    hint = SPHERE_HINTS.get(sphere, "")
    text = (
        f"{base_text}\n\n"
        f"{question['question']}\n\n"
        f"Можно ориентироваться на примеры: ({hint})"
    )
    await bot.send_message(chat_id=chat_id, text=text)


async def start_balance_wheel(message):
    user = message.from_user
    if not user:
        return

    user_id = user.id
    bot = message.get_bot()

    state = {
        "sphere_index": 0,
        "question_index": 0,
        "answers": {},
        "awaiting_resource": False,
        "finished": False,
        "wheel_sent": False,
    }
    _set_state(user_id, state)

    await bot.send_message(
        chat_id=message.chat_id,
        text="Колесо баланса",
    )

    await _send_current_step(message.chat_id, user_id, bot)


async def handle_balance_wheel_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    if not update.message or not update.effective_user:
        return False

    user_id = update.effective_user.id
    state = _get_state(user_id)
    if not state:
        return False

    if state.get("awaiting_resource"):
        return False

    if state.get("finished"):
        return True

    question = _current_question(state)
    sphere = _current_sphere(state)

    if question is None:
        await _finish_wheel(update.effective_chat.id, user_id, context.bot)
        return True

    if question["type"] != "text":
        return False

    answer_text = (update.message.text or "").strip()
    if not answer_text:
        await update.message.reply_text("Напиши ответ обычным сообщением.")
        return True

    state["answers"].setdefault(
        sphere,
        {
            "summary_lines": [f"Сфера {state['sphere_index'] + 1} из {len(SPHERES)}: {sphere}", ""],
            "satisfaction": 1,
            "importance": 1,
            "action": 1,
            "meaning": "",
        },
    )
    state["answers"][sphere]["meaning"] = answer_text
    _append_history(state, question["question"], answer_text)

    finished_this_sphere_text = _get_sphere_summary(state, sphere)
    await update.message.reply_text(finished_this_sphere_text)

    _advance(state)
    _set_state(user_id, state)

    if _is_finished(state):
        await _finish_wheel(update.effective_chat.id, user_id, context.bot)
        return True

    await _send_current_step(update.effective_chat.id, user_id, context.bot)
    return True


async def handle_balance_wheel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    query = update.callback_query
    user = update.effective_user

    if not query or not user:
        return False

    data = query.data or ""
    user_id = user.id
    state = _get_state(user_id)
    if not state:
        return False

    if state.get("finished") and not data.startswith("bw_resource:") and data != "bw_find_resource":
        return True

    if data.startswith("bw_choice:"):
        question = _current_question(state)
        sphere = _current_sphere(state)

        if question is None or question["type"] != "choice" or sphere is None:
            return True

        idx = int(data.split(":")[1])
        answer_text = question["options"][idx]
        score = question["scores"][idx]

        state["answers"].setdefault(
            sphere,
            {
                "summary_lines": [f"Сфера {state['sphere_index'] + 1} из {len(SPHERES)}: {sphere}", ""],
                "satisfaction": 1,
                "importance": 1,
                "action": 1,
                "meaning": "",
            },
        )

        state["answers"][sphere][question["key"]] = score
        _append_history(state, question["question"], answer_text)

        new_text = _get_sphere_summary(state, sphere)
        try:
            await query.edit_message_text(new_text)
        except Exception:
            pass

        _advance(state)
        _set_state(user_id, state)

        if _is_finished(state):
            await _finish_wheel(update.effective_chat.id, user_id, context.bot)
            return True

        await _send_current_step(update.effective_chat.id, user_id, context.bot)
        return True

    if data == "bw_find_resource":
        state["awaiting_resource"] = True
        _set_state(user_id, state)

        try:
            await query.edit_message_reply_markup(reply_markup=None)
        except Exception:
            pass

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="В какой сфере у тебя сейчас больше всего энергии?",
            reply_markup=_build_resource_keyboard(),
        )
        return True

    if data.startswith("bw_resource:"):
        idx = int(data.split(":")[1])
        resource_area = SPHERES[idx]

        try:
            await query.edit_message_text(
                text=f"В какой сфере у тебя сейчас больше всего энергии?\nОтвет: {resource_area}"
            )
        except Exception:
            pass

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Твой ресурс сейчас: {resource_area}",
        )

        _clear_state(user_id)
        return True

    return False


async def _finish_wheel(chat_id: int, user_id, bot):
    state = _get_state(user_id)
    if not state:
        return

    if state.get("wheel_sent"):
        return

    state["finished"] = True
    state["wheel_sent"] = True
    _set_state(user_id, state)

    image_path = None

    try:
        chart_data = {}
        for sphere in SPHERES:
            values = state["answers"].get(sphere, {})
            chart_data[sphere] = values.get("satisfaction", 1)

        image_path = generate_wheel(chart_data)

        if not image_path or not os.path.exists(image_path):
            raise RuntimeError("Колесо не построилось")

        with open(image_path, "rb") as file:
            await bot.send_photo(chat_id=chat_id, photo=file)

        await bot.send_message(
            chat_id=chat_id,
            text="Посмотри на свою картину жизни.",
            reply_markup=_build_find_resource_keyboard(),
        )
        return

    except Exception:
        await bot.send_message(
            chat_id=chat_id,
            text="Колесо не построилось.",
        )
        _clear_state(user_id)
        return

    finally:
        try:
            if image_path and os.path.exists(image_path):
                os.remove(image_path)
        except Exception:
            pass
