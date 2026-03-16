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


def get_option_text(option):
    return option["text"]


def get_option_value(option):
    return option["value"]


def calculate_total_score(answer_values):
    return sum(ANXIETY_SCORES[value] for value in answer_values)


def get_main_level_by_score(total_score):
    if 20 <= total_score <= 34:
        return "low"
    if 35 <= total_score <= 49:
        return "medium"
    if 50 <= total_score <= 64:
        return "high"
    return "very_high"


def calculate_profile(answer_values):
    counts = Counter(answer_values)

    for key in ANXIETY_LABELS:
        if key not in counts:
            counts[key] = 0

    total_answers = sum(counts.values()) or 1

    percentages = {
        key: round(counts[key] / total_answers * 100)
        for key in ANXIETY_LABELS
    }

    sorted_profile = sorted(
        percentages.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    return percentages, sorted_profile


def build_main_text(level_key):
    texts = {
        "low": (
            "Сейчас тревога не управляет вашим внутренним фоном.\n"
            "Даже при неопределённости вы чаще сохраняете опору, способность думать ясно и не перегружать себя лишними сценариями."
        ),
        "medium": (
            "Тревога у вас присутствует как заметный фон, но пока не захватывает всё пространство.\n"
            "В напряжённые моменты она может усиливаться, влиять на мысли, сомнения и внутреннее напряжение, но опора у вас сохраняется."
        ),
        "high": (
            "Тревога уже заметно влияет на ваше состояние.\n"
            "Она может включаться не только в сложных ситуациях, но и фоном: через ожидание проблем, внутреннее напряжение, прокручивание мыслей и трудность полностью выдохнуть."
        ),
        "very_high": (
            "Сейчас тревога занимает много внутреннего пространства.\n"
            "Она может влиять на тело, концентрацию, решения и ощущение безопасности, из-за чего даже обычные ситуации переживаются как перегрузка или скрытая угроза."
        ),
    }
    return texts[level_key]


def build_second_layer_text(level_key):
    texts = {
        "low": (
            "Во втором слое видно, что часть вас всё ещё умеет сохранять спокойствие, "
            "даже если в отдельных ситуациях тревога усиливается."
        ),
        "medium": (
            "Во втором слое видно привычное внутреннее волнение, которое становится заметнее "
            "в ситуациях ожидания, неопределённости или перегруза."
        ),
        "high": (
            "Во втором слое видно, что напряжение у вас может быстро нарастать "
            "и переходить из обычного волнения в устойчивую тревожную реакцию."
        ),
        "very_high": (
            "Во втором слое видно, что за тревогой может стоять уже не только напряжение, "
            "но и накопленная внутренняя перегрузка или истощение."
        ),
    }
    return texts[level_key]


def build_growth_text(level_key):
    texts = {
        "low": (
            "Ваша точка роста — не игнорировать тревогу полностью, "
            "а замечать её как ранний сигнал в действительно важных ситуациях."
        ),
        "medium": (
            "Ваша точка роста — раньше замечать момент, когда обычное волнение начинает превращаться "
            "в внутренний перегруз, и возвращать себе опору до усиления тревоги."
        ),
        "high": (
            "Ваша точка роста — учиться отделять реальные риски от тревожных сценариев "
            "и раньше снижать внутреннее напряжение, пока оно не стало постоянным фоном."
        ),
        "very_high": (
            "Ваша точка роста — не пытаться всё выдерживать только усилием воли, "
            "а выстраивать систему восстановления, снижения перегрузки и возвращения чувства безопасности."
        ),
    }
    return texts[level_key]


def build_profile_block(percentages):
    order = ["low", "medium", "high", "very_high"]
    lines = []

    for key in order:
        lines.append(f"{ANXIETY_LABELS[key]} — {percentages[key]}%")

    return "\n".join(lines)


def build_result(answer_values):
    total_score = calculate_total_score(answer_values)
    main_level = get_main_level_by_score(total_score)

    percentages, sorted_profile = calculate_profile(answer_values)

    second_layer_candidates = [
        item for item in sorted_profile if item[0] != main_level
    ]
    second_layer_key = second_layer_candidates[0][0] if second_layer_candidates else main_level

    return (
        f"🟡 *УРОВЕНЬ ТРЕВОГИ: {ANXIETY_LABELS[main_level].upper()}*\n\n"
        f"{build_main_text(main_level)}\n\n"
        f"📊 *ВАШ ПРОФИЛЬ РЕАКЦИЙ*\n"
        f"{build_profile_block(percentages)}\n\n"
        f"🌙 *ВТОРОЙ СЛОЙ*\n"
        f"{ANXIETY_LABELS[second_layer_key]}\n"
        f"{build_second_layer_text(second_layer_key)}\n\n"
        f"🌱 *ТОЧКА РОСТА*\n"
        f"{build_growth_text(main_level)}"
    )


TEST_DEF = {
    "key": "anxiety",
    "title": "Уровень тревоги",
    "intro_text": (
        "🟡 *Уровень тревоги*\n\n"
        "Этот тест помогает увидеть, насколько тревога влияет на ваше внутреннее состояние, мысли и повседневные реакции.\n\n"
        "*Как отвечать:*\n"
        "Читайте вопрос и выбирайте тот вариант, который ближе всего вам."
    ),
    "questions": questions,
    "get_option_text": get_option_text,
    "get_option_value": get_option_value,
    "build_result": build_result,
}
