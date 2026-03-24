from collections import Counter
from tests.scale import SCALE
from tests.archetype.questions import questions

ARCHETYPE_LABELS = {
    "leader": "Лидер",
    "observer": "Наблюдатель",
    "support": "Поддержка",
    "freedom": "Свобода",
}


def calculate_profile(answer_pairs):
    counts = Counter()

    for question, answer_value in answer_pairs:
        axis = question["axis"]
        counts[axis] += answer_value

    for key in ARCHETYPE_LABELS:
        if key not in counts:
            counts[key] = 0

    main_type = max(counts, key=counts.get)
    return main_type


def build_result(answer_pairs):
    main_type = calculate_profile(answer_pairs)
    main_label = ARCHETYPE_LABELS[main_type]

    if main_type == "leader":
        text = (
            "Вы чаще проявляетесь через влияние, инициативу и движение вперёд.\n\n"
            "Обычно вам проще включаться там, где нужно брать ответственность и вести."
        )
    elif main_type == "observer":
        text = (
            "Вы чаще проявляетесь через наблюдение, анализ и внутреннюю глубину.\n\n"
            "Обычно вам важно сначала понять суть, а уже потом действовать."
        )
    elif main_type == "support":
        text = (
            "Вы чаще проявляетесь через поддержку, тепло и контакт с людьми.\n\n"
            "Обычно рядом с вами другим становится спокойнее и понятнее."
        )
    else:
        text = (
            "Вы чаще проявляетесь через самостоятельность, свободу и внутреннюю дистанцию.\n\n"
            "Обычно вам важно сохранять пространство для себя и своих решений."
        )

    return (
        f"🧭 *Ваш архетип личности — {main_label.upper()}*\n\n"
        f"{text}"
    )


def build_profile_payload(answer_pairs):
    main_type = calculate_profile(answer_pairs)
    main_label = ARCHETYPE_LABELS[main_type]

    return {
        "test_key": "archetype",
        "title": "Архетип личности",
        "main_type": main_type,
        "main_label": main_label,
    }


def build_offer_text(profile_payload):
    return (
        "Вы уже увидели свой архетип.\n\n"
        "Но это только верхний слой.\n\n"
        "Глубже проявляются:\n"
        "— скрытые мотивации\n"
        "— повторяющиеся роли\n"
        "— сценарии, по которым вы живёте\n\n"
    )


TEST_DEF = {
    "key": "archetype",
    "title": "Архетип личности",
    "intro_text": "",
    "question_bank": questions,
    "scale": SCALE,
    "get_question_text": lambda question: question["text"],
    "build_result": build_result,
    "build_profile_payload": build_profile_payload,
    "build_offer_text": build_offer_text,
    "result_button_text": "Разобрать мой архетип",
}
