from collections import Counter
from tests.anxiety.questions import questions

ANXIETY_LABELS = {
    "low": "Низкий",
    "medium": "Умеренный",
    "high": "Высокий",
    "very_high": "Очень высокий",
}

ANXIETY_SCORES = {
    "low": 1,
    "medium": 2,
    "high": 3,
    "very_high": 4,
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

    second_type = sorted_profiles[1][0]
    score = sum(ANXIETY_SCORES[value] for value in answer_values)

    if 20 <= score <= 34:
        main_type = "low"
    elif 35 <= score <= 49:
        main_type = "medium"
    elif 50 <= score <= 64:
        main_type = "high"
    else:
        main_type = "very_high"

    return percentages, main_type, second_type, score


def build_summary(main_type):
    if main_type == "low":
        return "Сейчас внутреннее напряжение не управляет вашим фоном и не забирает много сил."

    if main_type == "medium":
        return "Внутреннее напряжение заметно присутствует, но пока не захватывает всё пространство."

    if main_type == "high":
        return "Внутреннее напряжение уже заметно влияет на ваше состояние, мысли и реакции."

    return "Сейчас внутреннее напряжение занимает много внутреннего пространства и влияет на ощущение опоры."


def build_main_text(main_type):
    if main_type == "low":
        return (
            "Даже при неопределённости вы чаще сохраняете опору, способность думать ясно "
            "и не перегружать себя лишними сценариями."
        )

    if main_type == "medium":
        return (
            "В напряжённые моменты оно может усиливаться, влиять на мысли, сомнения "
            "и внутреннее напряжение, но опора у вас сохраняется."
        )

    if main_type == "high":
        return (
            "Оно может включаться не только в сложных ситуациях, но и фоном: "
            "через ожидание проблем, внутреннее напряжение, прокручивание мыслей "
            "и трудность полностью выдохнуть."
        )

    return (
        "Оно может влиять на тело, концентрацию, решения и ощущение безопасности, "
        "из-за чего даже обычные ситуации переживаются как перегрузка или скрытая угроза."
    )


def build_second_text(second_type):
    if second_type == "low":
        return (
            "Во втором слое видно, что часть вас всё ещё умеет сохранять спокойствие, "
            "даже если в отдельных ситуациях напряжение усиливается."
        )

    if second_type == "medium":
        return (
            "Во втором слое видно привычное внутреннее волнение, которое становится заметнее "
            "в ситуациях ожидания, неопределённости или перегруза."
        )

    if second_type == "high":
        return (
            "Во втором слое видно, что напряжение у вас может быстро нарастать "
            "и переходить из обычного волнения в устойчивую тревожную реакцию."
        )

    return (
        "Во втором слое видно, что за напряжением может стоять уже не только тревога, "
        "но и накопленная внутренняя перегрузка или истощение."
    )


def build_growth_text(main_type):
    if main_type == "low":
        return (
            "Ваша точка роста — не игнорировать напряжение полностью, "
            "а замечать его как ранний сигнал в действительно важных ситуациях."
        )

    if main_type == "medium":
        return (
            "Ваша точка роста — раньше замечать момент, когда обычное волнение начинает "
            "превращаться во внутренний перегруз, и возвращать себе опору до усиления напряжения."
        )

    if main_type == "high":
        return (
            "Ваша точка роста — учиться отделять реальные риски от тревожных сценариев "
            "и раньше снижать внутреннее напряжение, пока оно не стало постоянным фоном."
        )

    return (
        "Ваша точка роста — не пытаться всё выдерживать только усилием воли, "
        "а выстраивать систему восстановления, снижения перегрузки и возвращения чувства безопасности."
    )


def build_result(answer_values):
    percentages, main_type, second_type, score = calculate_profile(answer_values)

    return (
        f"⚡ *УРОВЕНЬ ВНУТРЕННЕГО НАПРЯЖЕНИЯ*\n\n"
        f"*{ANXIETY_LABELS[main_type].upper()}*\n\n"
        f"{build_summary(main_type)}\n\n"
        f"{build_main_text(main_type)}\n\n"
        f"━━━━━━━━━━━━━━\n\n"
        f"*ПРОФИЛЬ РЕАКЦИЙ*\n"
        f"Низкий — {percentages['low']}%\n"
        f"Умеренный — {percentages['medium']}%\n"
        f"Высокий — {percentages['high']}%\n"
        f"Очень высокий — {percentages['very_high']}%\n\n"
        f"🌙 *ВТОРОЙ СЛОЙ*\n"
        f"*{ANXIETY_LABELS[second_type].upper()}*\n"
        f"{build_second_text(second_type)}\n\n"
        f"🌱 *ТОЧКА РОСТА*\n"
        f"{build_growth_text(main_type)}"
    )


def build_profile_payload(answer_values):
    percentages, main_type, second_type, score = calculate_profile(answer_values)
    raw_text = build_result(answer_values)

    return {
        "test_key": "anxiety",
        "title": "Уровень внутреннего напряжения",
        "main_type": main_type,
        "main_label": ANXIETY_LABELS[main_type],
        "second_type": second_type,
        "second_label": ANXIETY_LABELS[second_type],
        "percentages": percentages,
        "summary": build_summary(main_type),
        "growth_point": build_growth_text(main_type),
        "risk_zone": build_second_text(second_type),
        "raw_text": raw_text,
        "score": score,
    }


TEST_DEF = {
    "key": "anxiety",
    "title": "Уровень внутреннего напряжения",
    "intro_text": (
        "Уровень внутреннего напряжения\n\n"
        "Даже когда внешне всё спокойно,\n"
        "внутри может накапливаться напряжение.\n\n"
        "Оно влияет на мысли, решения\n"
        "и реакции на события.\n\n"
        "Этот тест поможет понять,\n"
        "насколько внутреннее напряжение\n"
        "сейчас влияет на ваше состояние.\n\n"
        "Тест займёт около 1–2 минут."
    ),
    "questions": questions,
    "get_option_text": lambda option: option["text"],
    "get_option_value": lambda option: option["value"],
    "build_result": build_result,
    "build_profile_payload": build_profile_payload,
}
