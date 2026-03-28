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
    idx = state["question_index"]
    if idx < 0 or idx >= len(QUESTIONS):
        return None
    return QUESTIONS[idx]


def _build_choice_keyboard(options):
    rows = []
    for idx, option in enumerate(options):
        rows.append([InlineKeyboardButton(option, callback_data=f"bw_choice:{idx}")])
    return InlineKeyboardMarkup(rows)


def _advance(state: dict):
    state["question_index"] += 1
    if state["question_index"] >= len(QUESTIONS):
        state["question_index"] = 0
        state["sphere_index"] += 1


def _ensure_sphere_data(state: dict, sphere: str):
    if sphere not in state["answers"]:
        state["answers"][sphere] = {
            "summary_lines": [f"Сфера {state['sphere_index'] + 1} из {len(SPHERES)}: {sphere}", ""],
            "satisfaction": 1,
            "importance": 1,
            "action": 1,
            "meaning": "",
        }


def _append_summary(state: dict, sphere: str, question_text: str, answer_text: str):
    _ensure_sphere_data(state, sphere)
    state["answers"][sphere]["summary_lines"].append(question_text)
    state["answers"][sphere]["summary_lines"].append(f"Ответ: {answer_text}")
    state["answers"][sphere]["summary_lines"].append("")


def _get_summary_text(state: dict, sphere: str) -> str:
    _ensure_sphere_data(state, sphere)
    return "\n".join(state["answers"][sphere]["summary_lines"]).strip()


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

    _ensure_sphere_data(state, sphere)
    summary_text = _get_summary_text(state, sphere)

    if question["type"] == "choice":
        text = f"{summary_text}\n\n{question['question']}"
        await bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=_build_choice_keyboard(question["options"]),
        )
        return

    hint = SPHERE_HINTS.get(sphere, "")
    text = (
        f"{summary_text}\n\n"
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

    if state.get("finished"):
        return True

    question = _current_question(state)
    sphere = _current_sphere(state)

    if question is None or sphere is None:
        await _finish_wheel(update.effective_chat.id, user_id, context.bot)
        return True

    if question["type"] != "text":
        return False

    answer_text = (update.message.text or "").strip()
    if not answer_text:
        await update.message.reply_text("Напиши ответ обычным сообщением.")
        return True

    _ensure_sphere_data(state, sphere)
    state["answers"][sphere]["meaning"] = answer_text
    _append_summary(state, sphere, question["question"], answer_text)

    finished_sphere_text = _get_summary_text(state, sphere)
    await update.message.reply_text(finished_sphere_text)

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

    if state.get("finished"):
        return True

    if not data.startswith("bw_choice:"):
        return False

    sphere = _current_sphere(state)
    question = _current_question(state)

    if sphere is None or question is None:
        await _finish_wheel(update.effective_chat.id, user_id, context.bot)
        return True

    if question["type"] != "choice":
        return True

    idx = int(data.split(":")[1])
    answer_text = question["options"][idx]
    score = question["scores"][idx]

    _ensure_sphere_data(state, sphere)
    state["answers"][sphere][question["key"]] = score
    _append_summary(state, sphere, question["question"], answer_text)

    try:
        await query.edit_message_text(_get_summary_text(state, sphere))
    except Exception:
        pass

    _advance(state)
    _set_state(user_id, state)

    if _is_finished(state):
        await _finish_wheel(update.effective_chat.id, user_id, context.bot)
        return True

    await _send_current_step(update.effective_chat.id, user_id, context.bot)
    return True


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

    except Exception:
        await bot.send_message(chat_id=chat_id, text="Колесо не построилось.")
    finally:
        try:
            if image_path and os.path.exists(image_path):
                os.remove(image_path)
        except Exception:
            pass

        _clear_state(user_id)
