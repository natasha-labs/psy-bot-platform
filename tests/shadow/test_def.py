from collections import Counter
from tests.shadow.questions import questions


SHADOW_DISPLAY_TYPES = {
    "control": "Контролёр",
    "weakness": "Ранимый",
    "anger": "Бунтарь",
    "fear": "Стратег",
}

BOT_LINK = "https://t.me/KodLichnostiBot"


def get_option_text(option):
    return option["text"]


def get_option_value(option):
    return option["value"]


def calculate_profile(answer_values):
    counts = Counter(answer_values)

    for key in SHADOW_DISPLAY_TYPES:
        if key not in counts:
            counts[key] = 0

    total = sum(counts.values()) or 1

    percentages = {
        key: round(counts[key] / total * 100)
        for key in SHADOW_DISPLAY_TYPES
    }

    sorted_profiles = sorted(
        percentages.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    main_type = sorted_profiles[0][0]
    second_type = sorted_profiles[1][0]

    return percentages, main_type, second_type, sorted_profiles


def build_type_description(main_type):
    if main_type == "control":
        return (
            "Этот тип Тени связан с сильной внутренней потребностью держать ситуацию под контролем.\n\n"
            "Внутри может быть много напряжения и ощущение, что расслабляться опасно. "
            "Контролёр часто старается управлять ситуацией, людьми или своими эмоциями, "
            "чтобы не столкнуться с хаосом или уязвимостью."
        )

    if main_type == "weakness":
        return (
            "Этот тип Тени связан с глубокой чувствительностью и той частью вас, "
            "которую долго приходилось прятать, чтобы не быть слишком открытым или беззащитным.\n\n"
            "Снаружи это может выглядеть как спокойствие или сдержанность, "
            "а внутри жить ранимость, потребность в бережности и страх быть уязвимо увиденным."
        )

    if main_type == "anger":
        return (
            "Этот тип Тени связан с подавленной злостью, силой и внутренним протестом.\n\n"
            "Бунтарская часть появляется там, где слишком долго приходилось терпеть, "
            "сдерживаться или не позволять себе открыто защищать границы."
        )

    return (
        "Этот тип Тени связан со скрытой настороженностью, внутренним напряжением и ожиданием угрозы.\n\n"
        "Стратегическая часть помогает заранее считывать риски и не терять осторожность, "
        "но в напряжённые периоды может усиливать тревогу и ощущение небезопасности."
    )


def build_second_interpretation(second_type):
    if second_type == "control":
        return (
            "Во втором слое у вас есть контролирующая часть: она включается там, где важно удержать ситуацию, "
            "не распасться и не потерять опору."
        )

    if second_type == "weakness":
        return (
            "Во втором слое у вас есть ранимая часть: она связана с чувствительностью, "
            "уязвимостью и потребностью быть бережно увиденным."
        )

    if second_type == "anger":
        return (
            "Во втором слое у вас есть бунтарская часть: в ней живёт энергия протеста, "
            "силы и желание не позволять давить на себя."
        )

    return (
        "Во втором слое у вас есть стратегическая часть: она помогает заранее считывать риски, "
        "замечать угрозы и не терять осторожность."
    )


def build_shadow_side(main_type):
    if main_type == "control":
        return (
            "В перекосе этот тип может уходить в жёсткость, перенапряжение и невозможность расслабиться, "
            "даже когда опасности уже нет."
        )

    if main_type == "weakness":
        return (
            "В перекосе этот тип может уходить в закрытость, болезненную чувствительность "
            "и страх открыто проявляться."
        )

    if main_type == "anger":
        return (
            "В перекосе этот тип может копить раздражение, взрываться слишком резко "
            "или видеть давление даже там, где его нет."
        )

    return (
        "В перекосе этот тип может жить в постоянной настороженности, ожидать угрозу заранее "
        "и терять чувство внутренней безопасности."
    )


def build_growth_text(main_type):
    if main_type == "control":
        return (
            "Точка роста — не только удерживать себя и ситуацию, но и замечать живые чувства под этим контролем."
        )

    if main_type == "weakness":
        return (
            "Точка роста — учиться видеть в уязвимости не слабость, а живую часть себя, "
            "которая тоже заслуживает места."
        )

    if main_type == "anger":
        return (
            "Точка роста — признавать злость как энергию границ и силы, "
            "а не только как угрозу отношениям."
        )

    return (
        "Точка роста — не бороться со страхом, а распознавать его как внутренний сигнал, "
        "которому тоже нужна опора."
    )


def build_profile_block(percentages):
    order = ["control", "weakness", "anger", "fear"]
    lines = []

    for key in order:
        lines.append(f"{SHADOW_DISPLAY_TYPES[key]} — {percentages[key]}%")

    return "\n".join(lines)


def build_share_text(main_type):
    shadow_type = SHADOW_DISPLAY_TYPES[main_type]
    return (
        f"Я прошёл тест «Код Тени».\n\n"
        f"Мой тип Тени — {shadow_type}\n\n"
        f"Интересно узнать, что скрывается в тебе.\n\n"
        f"Пройти тест:\n{BOT_LINK}"
    )


def build_result(answer_values):
    percentages, main_type, second_type, _sorted_profiles = calculate_profile(answer_values)

    main_type_name = SHADOW_DISPLAY_TYPES[main_type]
    second_type_name = SHADOW_DISPLAY_TYPES[second_type]

    text = (
        f"🌑 *ТВОЙ ТИП ТЕНИ*\n"
        f"{main_type_name}\n\n"
        f"{build_type_description(main_type)}\n\n"
        f"━━━━━━━━━━━━━━\n\n"
        f"📊 *ПРОФИЛЬ ТЕНИ*\n"
        f"{build_profile_block(percentages)}\n\n"
        f"━━━━━━━━━━━━━━\n\n"
        f"🌘 *ВТОРОЙ СЛОЙ ТЕНИ*\n"
        f"{second_type_name}\n"
        f"{build_second_interpretation(second_type)}\n\n"
        f"━━━━━━━━━━━━━━\n\n"
        f"⚠️ *РИСК ПЕРЕКОСА*\n"
        f"{build_shadow_side(main_type)}\n\n"
        f"🌱 *ТОЧКА РОСТА*\n"
        f"{build_growth_text(main_type)}\n\n"
        f"Тень не делает человека плохим.\n"
        f"Она показывает ту силу или чувствительность, которую психика когда-то научилась прятать."
    )

    return {
        "text": text,
        "share_text": build_share_text(main_type),
    }


TEST_DEF = {
    "key": "shadow",
    "title": "Код Тени",
    "intro_text": (
        "*Код Тени*\n\n"
        "У каждого человека есть сторона личности,\n"
        "которую он обычно не замечает.\n\n"
        "Иногда именно она влияет на наши реакции,\n"
        "конфликты и решения.\n\n"
        "Этот тест помогает увидеть\n"
        "вашу теневую сторону."
    ),
    "intro_button_text": "Начать тест",
    "questions": questions,
    "get_option_text": get_option_text,
    "get_option_value": get_option_value,
    "build_result": build_result,
}
