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

    total = sum(counts.values()) or 1

    percentages = {
        key: round(counts[key] / total * 100)
        for key in SHADOW_LABELS
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
    if main_type == "control":
        return "Ваша теневая сторона связана с потребностью держать себя, чувства и ситуацию под контролем."
    if main_type == "weakness":
        return "Ваша теневая сторона связана с глубокой чувствительностью и потребностью в эмоциональной безопасности."
    if main_type == "anger":
        return "Ваша теневая сторона связана с подавленной злостью, внутренним протестом и темой границ."
    return "Ваша теневая сторона связана с настороженностью, ожиданием угрозы и внутренней защитой."


def build_type_description(main_type):
    if main_type == "control":
        return (
            "Снаружи это может выглядеть как собранность и сила, а внутри часто жить напряжение "
            "и ощущение, что расслабляться опасно.\n\n"
            "Контроль становится способом удержать опору и не столкнуться с хаосом или уязвимостью."
        )
    if main_type == "weakness":
        return (
            "Снаружи это может выглядеть как спокойствие или сдержанность, "
            "а внутри жить ранимость, потребность в бережности и страх быть слишком открыто увиденным.\n\n"
            "Эта часть долго училась прятаться, чтобы не быть беззащитной."
        )
    if main_type == "anger":
        return (
            "Снаружи это может проявляться как резкость, раздражение или сопротивление давлению.\n\n"
            "Внутри здесь много силы, энергии протеста и желания не позволять нарушать ваши границы."
        )
    return (
        "Снаружи это может выглядеть как осторожность и собранность, "
        "а внутри жить постоянное считывание рисков и ожидание угрозы.\n\n"
        "Эта часть помогает выживать, но может удерживать психику в напряжении."
    )


def build_second_interpretation(second_type):
    if second_type == "control":
        return "Во втором слое у вас есть контролирующая часть: она включается там, где важно удержать ситуацию."
    if second_type == "weakness":
        return "Во втором слое у вас есть ранимая часть: она связана с чувствительностью и уязвимостью."
    if second_type == "anger":
        return "Во втором слое у вас есть бунтарская часть: в ней живёт энергия протеста и сила."
    return "Во втором слое у вас есть стратегическая часть: она помогает заранее считывать риски и угрозы."


def build_shadow_side(main_type):
    if main_type == "control":
        return "В перекосе этот тип может уходить в жёсткость, перенапряжение и невозможность расслабиться."
    if main_type == "weakness":
        return "В перекосе этот тип может уходить в закрытость, болезненную чувствительность и страх открыто проявляться."
    if main_type == "anger":
        return "В перекосе этот тип может копить раздражение, взрываться слишком резко или видеть давление даже там, где его нет."
    return "В перекосе этот тип может жить в постоянной настороженности и терять чувство внутренней безопасности."


def build_growth_point(main_type):
    if main_type == "control":
        return "Ваша точка роста — не только удерживать ситуацию, но и замечать живые чувства под этим контролем."
    if main_type == "weakness":
        return "Ваша точка роста — учиться видеть в уязвимости не слабость, а живую часть себя."
    if main_type == "anger":
        return "Ваша точка роста — признавать злость как энергию границ, а не только как угрозу."
    return "Ваша точка роста — не бороться со страхом, а распознавать его как важный внутренний сигнал."


def build_result(answer_pairs):
    percentages, main_type, second_type = calculate_profile(answer_pairs)

    return (
        f"🌑 *ТЕНЕВАЯ СТОРОНА*\n\n"
        f"*{SHADOW_LABELS[main_type].upper()}*\n\n"
        f"{build_summary(main_type)}\n\n"
        f"{build_type_description(main_type)}\n\n"
        f"━━━━━━━━━━━━━━\n\n"
        f"*ПРОФИЛЬ ТЕНИ*\n"
        f"Контролёр — {percentages['control']}%\n"
        f"Ранимый — {percentages['weakness']}%\n"
        f"Бунтарь — {percentages['anger']}%\n"
        f"Стратег — {percentages['fear']}%\n\n"
        f"🌘 *ВТОРОЙ СЛОЙ*\n"
        f"*{SHADOW_LABELS[second_type].upper()}*\n"
        f"{build_second_interpretation(second_type)}\n\n"
        f"⚠️ *РИСК ПЕРЕКОСА*\n"
        f"{build_shadow_side(main_type)}\n\n"
        f"🌱 *ТОЧКА РОСТА*\n"
        f"{build_growth_point(main_type)}"
    )


def build_profile_payload(answer_pairs):
    percentages, main_type, second_type = calculate_profile(answer_pairs)

    return {
        "test_key": "shadow",
        "title": "Код Тени",
        "main_type": main_type,
        "main_label": SHADOW_LABELS[main_type],
        "second_type": second_type,
        "second_label": SHADOW_LABELS[second_type],
        "percentages": percentages,
        "summary": build_summary(main_type),
        "growth_point": build_growth_point(main_type),
        "risk_zone": build_shadow_side(main_type),
        "raw_text": build_result(answer_pairs),
    }


TEST_DEF = {
    "key": "shadow",
    "title": "Код Тени",
    "intro_text": (
        "Код Тени\n\n"
        "У каждого человека есть сторона личности, которую он обычно не замечает.\n\n"
        "Этот тест поможет увидеть вашу теневую сторону."
    ),
    "question_bank": questions,
    "scale": SCALE,
    "get_question_text": lambda question: question["text"],
    "build_result": build_result,
    "build_profile_payload": build_profile_payload,
}
