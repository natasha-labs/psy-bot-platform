from tests.scale import SCALE
from tests.anxiety.questions import questions

ANXIETY_LABELS = {
    "low": "Низкий",
    "medium": "Умеренный",
    "high": "Высокий",
    "very_high": "Очень высокий",
}


def calculate_profile(answer_pairs):
    total_score = sum(answer_value for _, answer_value in answer_pairs)

    if total_score <= 26:
        return "low"
    if total_score <= 37:
        return "medium"
    if total_score <= 48:
        return "high"
    return "very_high"


def build_result(answer_pairs):
    main_type = calculate_profile(answer_pairs)
    level = ANXIETY_LABELS[main_type]

    if main_type == "low":
        body = (
            "Сейчас у вас нет выраженного внутреннего перегруза.\n\n"
            "Напряжение появляется, но не управляет вашим состоянием.\n\n"
            "Главное:\n"
            "вы тратите на тревогу меньше энергии, чем большинство людей."
        )
    elif main_type == "medium":
        body = (
            "Вы живёте с заметным внутренним напряжением, которое периодически усиливается.\n\n"
            "Чаще всего это проявляется так:\n"
            "— прокручивание мыслей\n"
            "— ожидание проблем\n"
            "— сложность расслабиться\n\n"
            "Главное:\n"
            "ваша тревога не в событиях, а в способе мышления."
        )
    elif main_type == "high":
        body = (
            "Вы живёте с постоянным внутренним напряжением, которое не всегда видно снаружи.\n\n"
            "Чаще всего это проявляется так:\n"
            "— прокручивание мыслей\n"
            "— ожидание проблем\n"
            "— сложность расслабиться\n\n"
            "Главное:\n"
            "ваша тревога не в событиях, а в способе мышления.\n\n"
            "Из-за этого вы тратите больше энергии, чем реально требуется."
        )
    else:
        body = (
            "Сейчас тревога управляет вашим внутренним состоянием сильнее, чем вам хотелось бы.\n\n"
            "Чаще всего это проявляется так:\n"
            "— внутренний перегруз\n"
            "— постоянное ожидание проблем\n"
            "— невозможность по-настоящему расслабиться\n\n"
            "Главное:\n"
            "тревога стала не реакцией, а фоном вашей жизни."
        )

    return f"⚡ *Ваш уровень тревоги — {level.upper()}*\n\n{body}"


def build_profile_payload(answer_pairs):
    main_type = calculate_profile(answer_pairs)
    main_label = ANXIETY_LABELS[main_type]

    return {
        "test_key": "anxiety",
        "title": "Тревога",
        "main_type": main_type,
        "main_label": main_label,
    }


def build_offer_text(profile_payload):
    return (
        "Вы уже увидели свой уровень тревоги.\n\n"
        "Но это только верхний слой.\n\n"
        "Тревога формируется глубже:\n"
        "— в привычках мышления\n"
        "— во внутренних реакциях\n"
        "— в скрытых паттернах\n\n"
    )


TEST_DEF = {
    "key": "anxiety",
    "title": "Тревога",
    "intro_text": "",
    "question_bank": questions,
    "scale": SCALE,
    "get_question_text": lambda question: question["text"],
    "build_result": build_result,
    "build_profile_payload": build_profile_payload,
    "build_offer_text": build_offer_text,
    "result_button_text": "Разобрать мою тревогу",
}
