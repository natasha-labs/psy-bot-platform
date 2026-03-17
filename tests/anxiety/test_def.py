from collections import Counter
from tests.scale import SCALE
from tests.anxiety.questions import questions

ANXIETY_LABELS = {
    "low": "Низкий",
    "medium": "Умеренный",
    "high": "Высокий",
    "very_high": "Очень высокий",
}


def calculate_profile(answer_pairs):
    scores = [answer_value for _, answer_value in answer_pairs]
    total_score = sum(scores)

    if total_score <= 26:
        main_type = "low"
    elif total_score <= 37:
        main_type = "medium"
    elif total_score <= 48:
        main_type = "high"
    else:
        main_type = "very_high"

    counts = Counter(scores)
    total_answers = len(scores) or 1

    percentages = {
        "low": round((counts.get(1, 0) + counts.get(2, 0) * 0.5) / total_answers * 100),
        "medium": round((counts.get(2, 0) * 0.5 + counts.get(3, 0)) / total_answers * 100),
        "high": round((counts.get(4, 0) + counts.get(5, 0) * 0.5) / total_answers * 100),
        "very_high": round((counts.get(5, 0) * 0.5) / total_answers * 100),
    }

    sorted_profiles = sorted(
        percentages.items(),
        key=lambda item: item[1],
        reverse=True,
    )
    second_type = sorted_profiles[1][0]

    return percentages, main_type, second_type, total_score


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
        return "Даже при неопределённости вы чаще сохраняете опору и не перегружаете себя лишними сценариями."
    if main_type == "medium":
        return "В напряжённые моменты оно может усиливаться, влиять на мысли и внутреннее напряжение, но опора у вас сохраняется."
    if main_type == "high":
        return "Оно может включаться фоном: через ожидание проблем, прокручивание мыслей и трудность полностью выдохнуть."
    return "Оно может влиять на тело, концентрацию, решения и ощущение безопасности, из-за чего даже обычные ситуации переживаются как перегрузка."


def build_second_text(second_type):
    if second_type == "low":
        return "Во втором слое видно, что часть вас всё ещё умеет сохранять спокойствие."
    if second_type == "medium":
        return "Во втором слое видно привычное внутреннее волнение, которое становится заметнее в ситуациях ожидания и перегруза."
    if second_type == "high":
        return "Во втором слое видно, что напряжение у вас может быстро нарастать и переходить в устойчивую тревожную реакцию."
    return "Во втором слое видно, что за напряжением может стоять уже не только тревога, но и накопленная перегрузка."


def build_growth_text(main_type):
    if main_type == "low":
        return "Ваша точка роста — не игнорировать напряжение полностью, а замечать его как ранний сигнал."
    if main_type == "medium":
        return "Ваша точка роста — раньше замечать момент, когда обычное волнение превращается во внутренний перегруз."
    if main_type == "high":
        return "Ваша точка роста — учиться отделять реальные риски от тревожных сценариев."
    return "Ваша точка роста — не пытаться всё выдерживать только усилием воли, а выстраивать систему восстановления."


def build_result(answer_pairs):
    percentages, main_type, second_type, total_score = calculate_profile(answer_pairs)

    return (
        f"⚡ *УРОВЕНЬ ТРЕВОГИ*\n\n"
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


def build_profile_payload(answer_pairs):
    percentages, main_type, second_type, total_score = calculate_profile(answer_pairs)

    return {
        "test_key": "anxiety",
        "title": "Уровень тревоги",
        "main_type": main_type,
        "main_label": ANXIETY_LABELS[main_type],
        "second_type": second_type,
        "second_label": ANXIETY_LABELS[second_type],
        "percentages": percentages,
        "summary": build_summary(main_type),
        "growth_point": build_growth_text(main_type),
        "risk_zone": build_second_text(second_type),
        "raw_text": build_result(answer_pairs),
        "score": total_score,
    }


TEST_DEF = {
    "key": "anxiety",
    "title": "Уровень тревоги",
    "intro_text": (
        "Уровень тревоги\n\n"
        "Этот тест помогает увидеть, насколько тревога влияет на ваше состояние, мысли и реакции."
    ),
    "question_bank": questions,
    "scale": SCALE,
    "get_question_text": lambda question: question["text"],
    "build_result": build_result,
    "build_profile_payload": build_profile_payload,
}
