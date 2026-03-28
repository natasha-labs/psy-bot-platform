import os
from typing import Dict, Any

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from tests.balance_wheel.questions import SPHERES
from tests.balance_wheel.logic import find_main_problem
from tests.balance_wheel.result import build_final_text

try:
    from storage.results_store import load_results, save_results
except Exception:
    load_results = None
    save_results = None

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

SATISFACTION_QUESTION = {
    "type": "choice",
    "key": "satisfaction",
    "question": "Насколько ты сейчас доволен этой сферой?",
    "options": ["Очень плохо", "Плохо", "Средне", "Хорошо", "Очень хорошо"],
    "scores": [1, 2, 3, 4, 5],
}

IMPORTANCE_QUESTION = {
    "type": "choice",
    "key": "importance",
    "question": "Насколько это важно для тебя?",
    "options": ["Не важно", "Скорее не важно", "Средне", "Важно", "Очень важно"],
    "scores": [1, 2, 3, 4, 5],
}

ACTION_QUESTION = {
    "type": "choice",
    "key": "action",
    "question": "Что ты сейчас делаешь для развития этой сферы?",
    "options": ["Я этим занимаюсь", "Иногда уделяю внимание", "Пока откладываю"],
    "scores": [3, 2, 1],
}

def _user_key(user_id) -> str:
    return str(user_id)

def is_balance_wheel_active(user_id) -> bool:
    state = BALANCE_WHEEL_STATE.get(_user_key(user_id))
    if not state:
        return False
    return not state.get("closed", False)

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

def _questions_for_sphere(sphere: str):
    hint = SPHERE_HINTS.get(sphere, "")
    text_question = {
        "type": "text",
        "key": "meaning",
        "question": (
            "Напиши несколько слов, что в этой сфере жизни для вас важно.\n\n"
            f"Можно ориентироваться на примеры: ({hint})"
        ),
    }
    return [
        SATISFACTION_QUESTION,
        IMPORTANCE_QUESTION,
        ACTION_QUESTION,
        text_question,
    ]

def _current_question(state: dict):
    sphere = _current_sphere(state)
    if sphere is None:
        return None
    questions = _questions_for_sphere(sphere)
    if state["question_index"] >= len(questions):
        return None
    return questions[state["question_index"]]

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
    if state["question_index"] >= 4:
        state["question_index"] = 0
        state["sphere_index"] += 1

def _save_balance_wheel_result(user_id, raw_data, main_problem=None, resource_area=None):
    if load_results is None or save_results is None:
        return

    try:
        data = load_results()
        uid = _user_key(user_id)

        if uid not in data:
            data[uid] = {
                "user_id": user_id,
                "completed_tests": [],
                "results": {},
                "paid_access": False,
            }

        if "results" not in data[uid]:
            data[uid]["results"] = {}

        data[uid]["results"]["balance_wheel"] = {
            "title": "Колесо баланса",
            "raw_data": raw_data,
            "main_problem": main_problem,
            "resource_area": resource_area,
        }

        save_results(data)
    except Exception:
        pass

def _choice_answer_text(question: dict, idx: int) -> str:
    return question["options"][idx]

async def _send_current_question(chat_id: int, user_id, bot):
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

    title = f"Сфера {state['sphere_index'] + 1} из {len(SPHERES)}: {sphere}"
    text = f"{title}\n\n{question['question']}"

    if question["type"] == "choice":
        await bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=_build_choice_keyboard(question["options"]),
        )
    else:
        await bot.send_message(
            chat_id=chat_id,
            text=text,
        )

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
        "wheel_sent": False,
        "closed": False,
    }
    _set_state(user_id, state)

    await bot.send_message(
        chat_id=message.chat_id,
        text="Колесо баланса\n\nМы пройдём по 9 сферам. В каждой сфере будет 3 вопроса с вариантами ответа и 1 короткий текстовый вопрос.",
    )

    await _send_current_question(message.chat_id, user_id, bot)

async def handle_balance_wheel_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    if not update.message or not update.effective_user:
        return False

    user_id = update.effective_user.id
    state = _get_state(user_id)
    if not state:
        return False

    if state.get("closed"):
        _clear_state(user_id)
        return False

    if state.get("awaiting_resource"):
        return False

    if state.get("wheel_sent"):
        return False

    if _is_finished(state):
        await _finish_wheel(update.effective_chat.id, user_id, context.bot)
        return True

    question = _current_question(state)
    if question is None:
        await _finish_wheel(update.effective_chat.id, user_id, context.bot)
        return True

    if question["type"] != "text":
        await update.message.reply_text("Используйте кнопки ниже.")
        return True

    answer_text = (update.message.text or "").strip()
    sphere = _current_sphere(state)

    if not answer_text:
        await update.message.reply_text("Напиши ответ обычным сообщением.")
        return True

    if sphere is None:
        await _finish_wheel(update.effective_chat.id, user_id, context.bot)
        return True

    state["answers"].setdefault(sphere, {})
    state["answers"][sphere]["meaning"] = answer_text

    _advance(state)
    _set_state(user_id, state)

    await _send_current_question(update.effective_chat.id, user_id, context.bot)
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

    if state.get("closed"):
        _clear_state(user_id)
        return False

    if data.startswith("bw_choice:"):
        if state.get("wheel_sent"):
            return True

        if _is_finished(state):
            await _finish_wheel(update.effective_chat.id, user_id, context.bot)
            return True

        question = _current_question(state)
        if question is None or question["type"] != "choice":
            return True

        idx = int(data.split(":")[1])
        score = question["scores"][idx]
        answer_text = _choice_answer_text(question, idx)
        sphere = _current_sphere(state)

        if sphere is None:
            await _finish_wheel(update.effective_chat.id, user_id, context.bot)
            return True

        state["answers"].setdefault(sphere, {})
        key = question["key"]

        if key == "satisfaction":
            state["answers"][sphere]["satisfaction"] = score
        elif key == "importance":
            state["answers"][sphere]["importance"] = score
        elif key == "action":
            state["answers"][sphere]["action"] = score

        try:
            await query.edit_message_text(
                text=(
                    f"Сфера {state['sphere_index'] + 1} из {len(SPHERES)}: {sphere}\n\n"
                    f"{question['question']}\n"
                    f"Ответ: {answer_text}"
                )
            )
        except Exception:
            pass

        _advance(state)
        _set_state(user_id, state)

        await _send_current_question(update.effective_chat.id, user_id, context.bot)
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
        main_problem = find_main_problem(state["answers"])

        _save_balance_wheel_result(
            user_id=user_id,
            raw_data=state["answers"],
            main_problem=main_problem,
            resource_area=resource_area,
        )

        try:
            await query.edit_message_text(
                text=f"В какой сфере у тебя сейчас больше всего энергии?\nОтвет: {resource_area}"
            )
        except Exception:
            pass

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=build_final_text(main_problem, resource_area),
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

    state["wheel_sent"] = True
    _set_state(user_id, state)

    image_path = None

    try:
        chart_data = {}
        for sphere in SPHERES:
            values = state["answers"].get(sphere, {})
            chart_data[sphere] = values.get("satisfaction", 1)

        image_path = generate_wheel(chart_data)

        if not image_path:
            raise RuntimeError("generate_wheel не вернул путь к файлу")

        if not os.path.exists(image_path):
            raise RuntimeError(f"Файл не найден: {image_path}")

        with open(image_path, "rb") as file:
            await bot.send_photo(
                chat_id=chat_id,
                photo=file,
            )

        await bot.send_message(
            chat_id=chat_id,
            text="Посмотри на свою картину жизни.",
            reply_markup=_build_find_resource_keyboard(),
        )

    except Exception as e:
        state["closed"] = True
        _set_state(user_id, state)
        await bot.send_message(
            chat_id=chat_id,
            text=f"Колесо не построилось: {type(e).__name__}: {e}",
        )
    finally:
        try:
            if image_path and os.path.exists(image_path):
                os.remove(image_path)
        except Exception:
            pass
