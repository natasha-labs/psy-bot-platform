from collections import Counter
from tests.anxiety.questions import questions


ANXIETY_LABELS = {
    "low": "Низкий",
    "medium": "Умеренный",
    "high": "Высокий",
    "very_high": "Очень высокий",
}


def calculate_profile(answer_values):
    counts = Counter(answer_values)

    for key in ANXIETY_LABELS:
        if key not in counts:
            counts[key] = 0

    total = sum(counts.values()) or 1

    percentages = {
        key: round(counts[key] / total * 100)
        for key in ANXIETY_LABELS
    }

    sorted_profiles = sorted(
        percentages.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    main_type = sorted_profiles[0][0]
    second_type = sorted_profiles[1][0]

    return percentages, main_type, second_type


def build_main_text(main_type):
    if main_type == "low":
        return (
            "Тревога обычно не занимает у вас центральное место.\n"
            "Вы чаще сохраняете внутреннюю устойчивость, даже когда вокруг есть неопределённость или нагрузка."
        )

    if main_type == "medium":
        return (
            "Тревога присутствует, но не захватывает вас полностью.\n"
            "Иногда она влияет на мысли, решения и внутреннее напряжение."
        )

    if main_type == "high":
        return (
            "Тревога заметно влияет на ваше внутреннее состояние.\n"
            "Может быть много фонового напряжения, ожидания сложностей и возврата к тревожным мыслям."
        )

    return (
        "Тревога сейчас выражена сильно.\n"
        "Она может занимать много внутреннего пространства, влиять на концентрацию, решения и ощущение опоры."
    )


def build_growth_text(main_type):
    if main_type == "low":
        return (
            "Ваша точка роста — не подавлять тревогу полностью, а замечать её как полезный сигнал, "
            "когда действительно важно замедлиться и внимательнее отнестись к ситуации."
        )

    if main_type == "medium":
        return (
            "Ваша точка роста — раньше замечать момент, когда обычное волнение начинает превращаться "
            "в внутреннюю перегрузку, и возвращать себе опору до того, как тревога усилится."
        )

    if main_type == "high":
        return (
            "Ваша точка роста — учиться разделять реальные риски и тревожные сценарии, "
            "чтобы не тратить слишком много энергии на внутреннее напряжение."
        )

    return (
        "Ваша точка роста — не пытаться всё время справляться усилием воли, "
        "а выстраивать для себя систему опоры, восстановления и снижения перегрузки."
    )


def build_second_text(second_type):
    if second_type == "low":
        return (
            "Второй слой показывает, что часть вас всё ещё умеет сохранять спокойствие и опору."
        )

    if second_type == "medium":
        return (
            "Второй слой показывает, что у вас есть привычный фон волнения, который периодически усиливается."
        )

    if second_type == "high":
        return (
            "Второй слой показывает, что напряжение и ожидание сложностей могут быстро нарастать."
        )

    return (
        "Второй слой показывает, что за тревогой может стоять сильная внутренняя перегрузка и истощение."
    )


def build_result(answer_values):
    percentages, main_type, second_type = calculate_profile(answer_values)

    return (
        f"🟡 **УРОВЕНЬ ТРЕВОГИ: {ANXIETY_LABELS[main_type].upper()}**\n\n"
        f"{build_main_text(main_type)}\n\n"
        f"📊 **ПРОФИЛЬ ТРЕВОГИ**\n"
        f"Низкий — {percentages['low']}%\n"
        f"Умеренный — {percentages['medium']}%\n"
        f"Высокий — {percentages['high']}%\n"
        f"Очень высокий — {percentages['very_high']}%\n\n"
        f"🌙 **ВТОРОЙ СЛОЙ**\n"
        f"{ANXIETY_LABELS[second_type]}\n"
        f"{build_second_text(second_type)}\n\n"
        f"🌱 **ТОЧКА РОСТА**\n"
        f"{build_growth_text(main_type)}"
    )


TEST_DEF = {
    "key": "anxiety",
    "title": "Уровень тревоги",
    "intro_text": (
        "🟡 **Уровень тревоги**\n\n"
        "Этот тест помогает увидеть, насколько тревога влияет на ваше внутреннее состояние, "
        "мысли и повседневные реакции.\n\n"
        "**Как отвечать:**\n"
        "Читайте вопрос и выбирайте тот вариант, который ближе всего вам."
    ),
    "questions": questions,
    "get_option_text": lambda option: option["text"],
    "get_option_value": lambda option: option["value"],
    "build_result": build_result,
}
