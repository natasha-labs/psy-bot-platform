from collections import Counter
from tests.archetype.questions import questions

ARCHETYPE_LABELS = {
    "leader": "Лидер",
    "observer": "Наблюдатель",
    "support": "Поддержка",
    "freedom": "Свобода",
}


def calculate_profile(answer_values):
    counts = Counter(answer_values)

    for key in ARCHETYPE_LABELS:
        if key not in counts:
            counts[key] = 0

    total = sum(counts.values()) or 1

    percentages = {
        key: round(counts[key] / total * 100)
        for key in ARCHETYPE_LABELS
    }

    sorted_profiles = sorted(
        percentages.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    main_type = sorted_profiles[0][0]
    second_type = sorted_profiles[1][0]

    return percentages, main_type, second_type


def build_summary(main_type):
    if main_type == "leader":
        return "Сильнее всего в вас проявляется стремление вести, влиять и задавать направление."

    if main_type == "observer":
        return "Сильнее всего в вас проявляется глубина, наблюдательность и внутренний анализ."

    if main_type == "support":
        return "Сильнее всего в вас проявляется тепло, контакт и способность быть опорой."

    return "Сильнее всего в вас проявляется независимость, потребность в свободе и верность себе."


def build_type_description(main_type):
    if main_type == "leader":
        return (
            "Вы естественно тянетесь к позиции, где можно брать ответственность, "
            "влиять на ситуацию и двигать процесс вперёд.\n\n"
            "Вам легче включаться, когда есть цель, направление и возможность принимать решения."
        )

    if main_type == "observer":
        return (
            "Вы чаще проявляетесь через наблюдение, понимание и внутреннюю глубину.\n\n"
            "Вам важно сначала почувствовать контекст, увидеть смысл и только потом действовать."
        )

    if main_type == "support":
        return (
            "Вы чаще проявляетесь через контакт, тепло и эмоциональную опору.\n\n"
            "Рядом с вами людям легче раскрываться, а ваша сила — в способности удерживать связь и поддержку."
        )

    return (
        "Вы чаще проявляетесь через самостоятельность, внутреннюю свободу и независимость.\n\n"
        "Для вас особенно важно не растворяться в чужих ожиданиях и сохранять связь с собой."
    )


def build_second_interpretation(second_type):
    if second_type == "leader":
        return (
            "Во втором слое у вас есть лидерская часть: она включается там, "
            "где нужно брать ответственность, влиять и собирать ситуацию вокруг себя."
        )

    if second_type == "observer":
        return (
            "Во втором слое у вас есть наблюдающая часть: она помогает видеть глубже, "
            "замечать скрытые мотивы и не действовать поверхностно."
        )

    if second_type == "support":
        return (
            "Во втором слое у вас есть поддерживающая часть: она связана с теплом, "
            "эмпатией и способностью быть для других точкой опоры."
        )

    return (
        "Во втором слое у вас есть свободная часть: она помогает сохранять независимость, "
        "не растворяться в ожиданиях и держать связь с собой."
    )


def build_shadow_side(main_type):
    if main_type == "leader":
        return (
            "В перекосе этот архетип может уходить в чрезмерный контроль, "
            "жёсткость и невозможность расслабиться."
        )

    if main_type == "observer":
        return (
            "В перекосе этот архетип может застревать в анализе, "
            "отдаляться от живого контакта и слишком долго не переходить к действию."
        )

    if main_type == "support":
        return (
            "В перекосе этот архетип может слишком сильно подстраиваться под других "
            "и терять контакт со своими собственными потребностями."
        )

    return (
        "В перекосе этот архетип может уходить в дистанцию, избегать привязанности "
        "и защищать свободу даже там, где нужна близость."
    )


def build_growth_point(main_type):
    if main_type == "leader":
        return "Ваша точка роста — не только вести, но и иногда разрешать себе не знать ответ сразу."

    if main_type == "observer":
        return "Ваша точка роста — не застревать в наблюдении и иногда идти в действие чуть раньше."

    if main_type == "support":
        return "Ваша точка роста — не забывать о себе, пока вы поддерживаете других."

    return "Ваша точка роста — не путать свободу с изоляцией и оставлять место для близости."


def build_result(answer_values):
    percentages, main_type, second_type = calculate_profile(answer_values)

    return (
        f"🧭 *АРХЕТИП ЛИЧНОСТИ*\n\n"
        f"*{ARCHETYPE_LABELS[main_type].upper()}*\n\n"
        f"{build_summary(main_type)}\n\n"
        f"{build_type_description(main_type)}\n\n"
        f"━━━━━━━━━━━━━━\n\n"
        f"*ПРОФИЛЬ АРХЕТИПА*\n"
        f"Лидер — {percentages['leader']}%\n"
        f"Наблюдатель — {percentages['observer']}%\n"
        f"Поддержка — {percentages['support']}%\n"
        f"Свобода — {percentages['freedom']}%\n\n"
        f"🌗 *ВТОРОЙ СЛОЙ*\n"
        f"*{ARCHETYPE_LABELS[second_type].upper()}*\n"
        f"{build_second_interpretation(second_type)}\n\n"
        f"⚠️ *РИСК ПЕРЕКОСА*\n"
        f"{build_shadow_side(main_type)}\n\n"
        f"🌱 *ТОЧКА РОСТА*\n"
        f"{build_growth_point(main_type)}"
    )


def build_profile_payload(answer_values):
    percentages, main_type, second_type = calculate_profile(answer_values)
    raw_text = build_result(answer_values)

    return {
        "test_key": "archetype",
        "title": "Архетип личности",
        "main_type": main_type,
        "main_label": ARCHETYPE_LABELS[main_type],
        "second_type": second_type,
        "second_label": ARCHETYPE_LABELS[second_type],
        "percentages": percentages,
        "summary": build_summary(main_type),
        "growth_point": build_growth_point(main_type),
        "risk_zone": build_shadow_side(main_type),
        "raw_text": raw_text,
    }


TEST_DEF = {
    "key": "archetype",
    "title": "Архетип личности",
    "intro_text": (
        "Архетип личности\n\n"
        "У каждого человека есть естественный стиль поведения —\n"
        "то, как он взаимодействует с людьми, решениями и жизнью.\n\n"
        "В психологии это называют архетипом личности.\n\n"
        "Этот тест поможет увидеть,\n"
        "какой архетип сейчас сильнее всего проявляется в вас.\n\n"
        "Тест займёт около 1–2 минут."
    ),
    "questions": questions,
    "get_option_text": lambda option: option["text"],
    "get_option_value": lambda option: option["value"],
    "build_result": build_result,
    "build_profile_payload": build_profile_payload,
}
