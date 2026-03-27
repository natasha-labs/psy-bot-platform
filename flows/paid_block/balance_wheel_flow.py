from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from tests.balance_wheel.questions import SPHERES, get_questions_for_sphere
from tests.balance_wheel.logic import find_main_problem
from tests.balance_wheel.result import build_final_text
from tests.balance_wheel.visual import generate_wheel


user_state = {}


async def start_balance_wheel(message: types.Message):
    user_state[message.from_user.id] = {
        "sphere_index": 0,
        "question_index": 0,
        "data": {}
    }

    await ask_next(message)


async def ask_next(message: types.Message):
    state = user_state[message.from_user.id]

    if state["sphere_index"] >= len(SPHERES):
        await finish_wheel(message)
        return

    sphere = SPHERES[state["sphere_index"]]
    questions = get_questions_for_sphere(sphere)

    question = questions[state["question_index"]]

    if question["type"] == "choice":
        keyboard = InlineKeyboardMarkup()
        for i, option in enumerate(question["options"]):
            keyboard.add(
                InlineKeyboardButton(
                    option,
                    callback_data=f"bw_{i}"
                )
            )
        await message.answer(question["question"], reply_markup=keyboard)
    else:
        await message.answer(question["question"])


async def handle_text(message: types.Message):
    state = user_state.get(message.from_user.id)
    if not state:
        return

    sphere = SPHERES[state["sphere_index"]]
    questions = get_questions_for_sphere(sphere)
    question = questions[state["question_index"]]

    if question["type"] == "text":
        state["data"].setdefault(sphere, {})
        state["data"][sphere]["meaning"] = message.text

        state["question_index"] += 1
        await ask_next(message)


async def handle_choice(callback: types.CallbackQuery):
    state = user_state.get(callback.from_user.id)
    if not state:
        return

    sphere = SPHERES[state["sphere_index"]]
    questions = get_questions_for_sphere(sphere)
    question = questions[state["question_index"]]

    index = int(callback.data.split("_")[1])
    score = question["scores"][index]

    state["data"].setdefault(sphere, {})

    if "satisfaction" in question["key"]:
        state["data"][sphere]["satisfaction"] = score
    elif "importance" in question["key"]:
        state["data"][sphere]["importance"] = score
    elif "action" in question["key"]:
        state["data"][sphere]["action"] = score

    state["question_index"] += 1

    if state["question_index"] >= 4:
        state["question_index"] = 0
        state["sphere_index"] += 1

    await callback.message.delete()
    await ask_next(callback.message)


async def finish_wheel(message: types.Message):
    state = user_state[message.from_user.id]
    data = state["data"]

    chart_data = {
        sphere: values["satisfaction"]
        for sphere, values in data.items()
    }

    image_path = generate_wheel(chart_data)

    await message.answer_photo(types.InputFile(image_path))

    keyboard = InlineKeyboardMarkup().add(
        InlineKeyboardButton("Найти ресурс", callback_data="find_resource")
    )

    await message.answer("Посмотри на свою картину жизни", reply_markup=keyboard)


async def handle_resource(callback: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup()

    for i, sphere in enumerate(SPHERES):
        keyboard.add(
            InlineKeyboardButton(sphere, callback_data=f"res_{i}")
        )

    await callback.message.answer(
        "В какой сфере у тебя сейчас больше всего энергии?",
        reply_markup=keyboard
    )


async def handle_resource_choice(callback: types.CallbackQuery):
    state = user_state[callback.from_user.id]
    data = state["data"]

    resource_index = int(callback.data.split("_")[1])
    resource_area = SPHERES[resource_index]

    main_problem = find_main_problem(data)

    text = build_final_text(main_problem, resource_area)

    await callback.message.delete()
    await callback.message.answer(text)
