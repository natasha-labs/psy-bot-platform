from collections import Counter
from tests.scale import SCALE
from tests.shadow.questions import questions

SHADOW_LABELS = {
    "control": "Контролёр",
    "weakness": "Ранимый",
    "anger": "Бунтарь",
    "fear": "Стратег",
}


def calculate_profile(answer_pairs):
    counts = Counter()

    for question, answer_value in answer_pairs:
        axis = question["axis"]
        counts[axis] += answer_value

    for key in SHADOW_LABELS:
        if key not in counts:
            counts[key] = 0

    main_type = max(counts, key=counts.get)
    return main_type


def build_result(answer_pairs):
    main_type = calculate_profile(answer_pairs)
    main_label = SHADOW_LABELS[main_type]

    if main_type == "control":
        text = (
            "Внутри вас сильно желание удерживать ситуацию под контролем.\n\n"
            "Чаще всего это проявляется так:\n"
            "— трудно доверять ходу событий\n"
            "— хочется всё держать в руках\n"
            "— напряжение растёт, когда что-то не под контролем"
        )
    elif main_type == "weakness":
        text = (
            "Внутри вас есть чувствительная часть, которую вы привыкли прятать.\n\n"
            "Чаще всего это проявляется так:\n"
            "— сложно показывать уязвимость\n"
            "— трудно просить помощи\n"
            "— переживания остаются внутри"
        )
    elif main_type == "anger":
        text = (
            "Внутри вас много сдержанной злости и напряжения на тему границ.\n\n"
            "Чаще всего это проявляется так:\n"
            "— раздражение копится внутри\n"
            "— трудно спокойно переносить давление\n"
            "— внутри быстро включается протест"
        )
    else:
        text = (
            "Внутри вас много настороженности и ожидания риска.\n\n"
            "Чаще всего это проявляется так:\n"
            "— сложно полностью расслабиться\n"
            "— есть внутреннее ожидание угрозы\n"
            "— хочется держать дистанцию"
        )

    return (
        f"🌑 *Ваш теневой профиль — {main_label.upper()}*\n\n"
        f"{text}"
    )


def build_profile_payload(answer_pairs):
    main_type = calculate_profile(answer_pairs)
    main_label = SHADOW_LABELS[main_type]

    return {
        "test_key": "shadow",
        "title": "Теневой профиль",
        "main_type": main_type,
        "main_label": main_label,
    }


def build_offer_text(profile_payload):
    return (
        "Вы уже увидели свой теневой профиль.\n\n"
        "Но это только верхний слой.\n\n"
        "Тень формируется глубже:\n"
        "— в защитных реакциях\n"
        "— в подавленных чувствах\n"
        "— в скрытых паттернах поведения\n\n"
        "Мы можем разобрать это персонально."
    )


TEST_DEF = {
    "key": "shadow",
    "title": "Теневой профиль",
    "intro_text": "",
    "question_bank": questions,
    "scale": SCALE,
    "get_question_text": lambda question: question["text"],
    "build_result": build_result,
    "build_profile_payload": build_profile_payload,
    "build_offer_text": build_offer_text,
    "result_button_text": "Разобрать мой теневой профиль",
}
