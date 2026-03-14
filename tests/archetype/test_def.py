from collections import Counter
from tests.archetype.questions import questions

ARCHETYPE_LABELS = {
    "leader": "Лидер",
    "observer": "Наблюдатель",
    "support": "Поддержка",
    "freedom": "Свобода",
}


def build_result(answer_values):
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

    return (
        f"✨ **ТВОЙ ТИП АРХЕТИПА**\n"
        f"{ARCHETYPE_LABELS[main_type]}\n\n"
        f"📊 **ПРОФИЛЬ АРХЕТИПА**\n"
        f"Лидер — {percentages['leader']}%\n"
        f"Наблюдатель — {percentages['observer']}%\n"
        f"Поддержка — {percentages['support']}%\n"
        f"Свобода — {percentages['freedom']}%\n\n"
        f"🌙 **ВТОРОЙ СЛОЙ АРХЕТИПА**\n"
        f"{ARCHETYPE_LABELS[second_type]}"
    )


TEST_DEF = {
    "key": "archetype",
    "title": "Архетип личности",
    "intro_text": (
        "✨ **Архетип личности**\n\n"
        "Этот тест помогает увидеть ваш ведущий стиль поведения, "
        "способ взаимодействия с миром и внутреннюю роль.\n\n"
        "**Как отвечать:**\n"
        "Читайте вопрос и выбирайте тот вариант, который ближе всего вам."
    ),
    "questions": questions,
    "get_option_text": lambda option: option["text"],
    "get_option_value": lambda option: option["value"],
    "build_result": build_result,
}
