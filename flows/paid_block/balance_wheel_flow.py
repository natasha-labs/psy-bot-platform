import os
from typing import Dict, Any

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from tests.balance_wheel.questions import SPHERES
from tests.balance_wheel.logic import find_main_problem
from tests.balance_wheel.result import build_final_text
from tests.balance_wheel.visual import generate_wheel

try:
    from storage.results_store import load_results, save_results
except Exception:
    load_results = None
    save_results = None


BALANCE_WHEEL_STATE: Dict[str, Dict[str, Any]] = {}


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


def _build_choice_keyboard(options):
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(opt, callback_data=f"bw:{i}")] for i, opt in enumerate(options)]
    )


def _advance(state: dict):
    state["question_index"] += 1
    if state["question_index"] >= 4:
        state["question_index"] = 0
        state["sphere_index"] += 1


def _get_questions():
    return [
        {
            "type": "choice",
            "key": "satisfaction",
            "q": "Насколько ты сейчас доволен этой сферой?",
            "opts": ["Очень плохо", "Плохо", "Средне", "Хорошо", "Очень хорошо"],
            "scores": [1, 2, 3, 4, 5],
        },
        {
            "type": "choice",
            "key": "importance",
            "q": "Насколько это важно для тебя?",
            "opts": ["Не важно", "Скорее не важно", "Средне", "Важно", "Очень важно"],
            "scores": [1, 2, 3, 4, 5],
        },
        {
            "type": "choice",
            "key": "action",
            "q": "Что ты сейчас делаешь для развития этой сферы?",
            "opts": ["Я этим занимаюсь", "Иногда уделяю внимание", "Пока откладываю"],
            "scores": [3, 2, 1],
        },
        {
            "type": "text",
            "key": "meaning",
            "q": "Напиши несколько слов, что важно в этой сфере",
        },
    ]


async def _send_question(chat_id, user_id, bot):
    state = _get_state(user_id)
    if not state:
        return

    if _is_finished(state):
        await _finish(chat_id, user_id, bot)
        return

    sphere = _current_sphere(state)
    q = _get_questions()[state["question_index"]]

    if q["type"] == "choice":
        await bot.send_message(
            chat_id=chat_id,
            text=f"{sphere}\n\n{q['q']}",
            reply_markup=_build_choice_keyboard(q["opts"]),
        )
    else:
        await bot.send_message(
            chat_id=chat_id,
            text=f"{sphere}\n\n{q['q']}",
        )


async def start_balance_wheel(message):
    user_id = message.from_user.id
    bot = message.get_bot()

    state = {
        "sphere_index": 0,
        "question_index": 0,
        "answers": {},
        "done": False,
    }

    _set_state(user_id, state)

    await bot.send_message(
        chat_id=message.chat_id,
        text="Колесо баланса",
    )

    await _send_question(message.chat_id, user_id, bot)


async def handle_balance_wheel_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    state = _get_state(user_id)

    if not state or state.get("done"):
        return False

    q = _get_questions()[state["question_index"]]

    if q["type"] != "text":
        return False

    sphere = _current_sphere(state)
    state["answers"].setdefault(sphere, {})
    state["answers"][sphere]["meaning"] = update.message.text

    _advance(state)
    _set_state(user_id, state)

    await _send_question(update.effective_chat.id, user_id, context.bot)
    return True


async def handle_balance_wheel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id

    if not query:
        return False

    data = query.data
    state = _get_state(user_id)

    if not state or state.get("done"):
        return False

    if not data.startswith("bw:"):
        return False

    idx = int(data.split(":")[1])
    q = _get_questions()[state["question_index"]]
    sphere = _current_sphere(state)

    state["answers"].setdefault(sphere, {})
    state["answers"][sphere][q["key"]] = q["scores"][idx]

    _advance(state)
    _set_state(user_id, state)

    await _send_question(update.effective_chat.id, user_id, context.bot)
    return True


async def _finish(chat_id, user_id, bot):
    state = _get_state(user_id)
    if not state:
        return

    if state.get("done"):
        return

    state["done"] = True
    _set_state(user_id, state)

    try:
        chart_data = {}
        for sphere in SPHERES:
            val = state["answers"].get(sphere, {}).get("satisfaction", 1)
            chart_data[sphere] = val

        path = generate_wheel(chart_data)

        with open(path, "rb") as f:
            await bot.send_photo(chat_id=chat_id, photo=f)

    except Exception as e:
        await bot.send_message(chat_id=chat_id, text=f"Ошибка: {e}")

    _clear_state(user_id)
