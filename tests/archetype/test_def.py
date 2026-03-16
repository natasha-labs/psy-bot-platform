from collections import Counter
from tests.archetype.questions import questions


ARCHETYPE_LABELS = {
    "leader": "Лидер",
    "observer": "Наблюдатель",
    "support": "Поддержка",
    "freedom": "Свобода",
}


def get_option_text(option):
    return option["text"]


def get_option_value(option):
    return option["value"]


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


def build_type_description(main_type):
    if main_type == "leader":
        return (
            "Этот архетип проявляется через действие, влияние и внутреннюю собранность.\n"
            "Человек с таким профилем чаще стремится вести, направлять и принимать решения."
        )

    if main_type == "observer":
        return (
            "Этот архетип проявляется через глубину, внимание и внутренний анализ.\n"
            "Человек с таким профилем чаще сначала замечает, понимает и только потом действует."
        )

    if main_type == "support":
        return (
            "Этот архетип проявляется через контакт, тепло и эмоциональную опору.\n"
            "Человек с таким профилем часто умеет поддерживать, объединять и создавать ощущение безопасности."
        )

    return (
        "Этот архетип проявляется через независимость, внутреннюю честность и потребность в свободе.\n"
        "Человеку с таким профилем важно сохранять пространство для себя и идти своим путём."
    )


def build_main_interpretation(main_type):
    if main_type == "leader":
        return "Лидерство и влияние"
    if main_type == "observer":
        return "Наблюдение и глубина"
    if main_type == "support":
        return "Поддержка и контакт"
    return "Свобода и дистанция"


def build_second_interpretation(second_type):
    if second_type == "leader":
        return (
            "Во втором слое у вас есть лидерская часть: она включается там, где нужно брать ответственность, влиять и собирать ситуацию вокруг себя."
        )

    if second_type == "observer":
        return (
            "Во втором слое у вас есть наблюдающая часть: она помогает видеть глубже, замечать скрытые мотивы и не действовать поверхностно."
        )

    if second_type == "support":
        return (
            "Во втором слое у вас есть поддерживающая часть: она связана с теплом, эмпатией и способностью быть для других точкой опоры."
        )

    return (
        "Во втором слое у вас есть свободная часть: она помогает сохранять независимость, не растворяться в ожиданиях и держать связь с собой."
    )


def build_shadow_side(main_type):
    if main_type == "leader":
        return (
            "В перекосе этот архетип может уходить в чрезмерный контроль, жёсткость и невозможность расслабиться."
        )

    if main_type == "observer":
        return (
            "В перекосе этот архетип может застревать в анализе, отдаляться от живого контакта и слишком долго не переходить к действию."
        )

    if main_type == "support":
        return (
            "В перекосе этот архетип может слишком сильно подстраиваться под других и терять контакт со своими собственными потребностями."
        )

    return (
        "В перекосе этот архетип может уходить в дистанцию, избегать привязанности и защищать свободу даже там, где нужна близость."
    )


def build_growth_text(main_type):
    if main_type == "leader":
        return "Не только вести, но и иногда разрешать себе не знать ответ сразу."
    if main_type == "observer":
        return "Не застревать в наблюдении и иногда идти в действие чуть раньше."
    if main_type == "support":
        return "Не забывать о себе, пока поддерживаете других."
    return "Не путать свободу с изоляцией и оставлять место для близости."


def build_result(answer_values):
    percentages, main_type, second_type = calculate_profile(answer_values)

    type_description = build_type_description(main_type)
    subtitle = build_main_interpretation(main_type)
    second_text = build_second_interpretation(second_type)
    shadow_text = build_shadow_side(main_type)

    profile_block = (
        f"Лидер — {percentages['leader']}%\n"
        f"Наблюдатель — {percentages['observer']}%\n"
        f"Поддержка — {percentages['support']}%\n"
        f"Свобода — {percentages['freedom']}%"
    )

    return (
        f"🧠 *РЕЗУЛЬТАТ ТЕСТА*\n\n"
        f"🔎 *ВАШ АРХЕТИП ЛИЧНОСТИ*\n"
        f"*{subtitle.upper()}*\n\n"
        f"{type_description}\n\n"
        f"━━━━━━━━━━━━━━\n\n"
        f"📊 *ПРОФИЛЬ АРХЕТИПА*\n"
        f"{profile_block}\n\n"
        f"━━━━━━━━━━━━━━\n\n"
        f"🌗 *ВТОРОЙ СЛОЙ АРХЕТИПА*\n"
        f"{ARCHETYPE_LABELS[second_type]}\n"
        f"{second_text}\n\n"
        f"━━━━━━━━━━━━━━\n\n"
        f"⚠️ *РИСК ПЕРЕКОСА*\n"
        f"{shadow_text}"
    )


def build_profile_payload(answer_values):
    percentages, main_type, second_type = calculate_profile(answer_values)

    return {
        "test_key": "archetype",
        "title": "Архетип личности",
        "main_type": main_type,
        "main_label": ARCHETYPE_LABELS[main_type],
        "second_type": second_type,
        "second_label": ARCHETYPE_LABELS[second_type],
        "percentages": percentages,
        "summary": build_type_description(main_type),
        "growth_point": build_growth_text(main_type),
        "risk_zone": build_shadow_side(main_type),
        "raw_text": build_result(answer_values),
        "dominant_theme": build_main_interpretation(main_type),
        "primary_result": main_type,
        "secondary_result": second_type,
        "profile_data": percentages,
    }


TEST_DEF = {
    "key": "archetype",
    "title": "Архетип личности",
    "intro_text": (
        "*Архетип личности*\n\n"
        "У каждого человека есть естественный стиль поведения —\n"
        "то, как он взаимодействует с людьми, решениями и жизнью.\n\n"
        "В психологии это называют архетипом личности.\n\n"
        "Этот тест поможет увидеть,\n"
        "какой архетип сейчас сильнее всего проявляется в вас.\n\n"
        "Тест займёт около 1–2 минут."
    ),
    "intro_button_text": "Начать тест",
    "questions": questions,
    "get_option_text": get_option_text,
    "get_option_value": get_option_value,
    "build_result": build_result,
    "build_profile_payload": build_profile_payload,
}
