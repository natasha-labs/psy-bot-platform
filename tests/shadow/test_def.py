from collections import Counter
from tests.shadow.questions import questions


SHADOW_DISPLAY_TYPES = {
    "control": "Контролёр",
    "weakness": "Отражатель",
    "anger": "Бунтарь",
    "fear": "Стратег",
}

BOT_LINK = "https://t.me/KodLichnostiBot"


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
            "чтобы не столкнуться с хаосом или уязвимостью.\n\n"
            "Что это может означать:\n"
            "• сложно доверять другим\n"
            "• есть привычка держать всё под контролем\n"
            "• напряжение появляется, когда ситуация выходит из-под контроля\n\n"
            "Точка роста:\n"
            "учиться отпускать контроль и позволять себе больше гибкости."
        )

    if main_type == "anger":
        return (
            "Этот тип Тени связан с подавленной злостью и сильной реакцией на давление.\n\n"
            "Бунтарь появляется тогда, когда человек долго сдерживает раздражение или не может "
            "открыто защищать свои границы. Внутри может накапливаться энергия протеста.\n\n"
            "Что это может означать:\n"
            "• сильная реакция на ограничения\n"
            "• раздражение, когда кто-то давит или контролирует\n"
            "• склонность резко реагировать в напряжённых ситуациях\n\n"
            "Точка роста:\n"
            "научиться выражать злость экологично и использовать её как энергию для защиты границ."
        )

    if main_type == "weakness":
        return (
            "Этот тип Тени связан с глубокой чувствительностью к людям и атмосфере вокруг.\n\n"
            "Отражатель тонко чувствует настроение других и может сильно переживать их реакции. "
            "Иногда это приводит к тому, что человек скрывает собственные чувства и подстраивается под окружающих.\n\n"
            "Что это может означать:\n"
            "• высокая эмоциональная чувствительность\n"
            "• склонность переживать из-за реакций других людей\n"
            "• желание не ранить и не расстроить окружающих\n\n"
            "Точка роста:\n"
            "учиться слышать свои чувства и не терять себя в ожиданиях других."
        )

    return (
        "Этот тип Тени связан со скрытой настороженностью и внутренней готовностью к угрозе.\n\n"
        "Стратег часто внимательно наблюдает за происходящим и пытается заранее просчитать возможные риски. "
        "Это может создавать ощущение постоянного внутреннего напряжения.\n\n"
        "Что это может означать:\n"
        "• повышенная настороженность\n"
        "• склонность ожидать проблемы заранее\n"
        "• желание держать дистанцию, чтобы не быть раненым\n\n"
        "Точка роста:\n"
        "развивать чувство безопасности и позволять себе больше доверия."
    )


def build_profile_block(sorted_profiles):
    lines = []
    for key, percent in sorted_profiles:
        lines.append(f"{SHADOW_DISPLAY_TYPES[key]} — {percent}%")
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
    percentages, main_type, second_type, sorted_profiles = calculate_profile(answer_values)

    main_type_name = SHADOW_DISPLAY_TYPES[main_type]
    second_type_name = SHADOW_DISPLAY_TYPES[second_type]
    type_description = build_type_description(main_type)
    profile_block = build_profile_block(sorted_profiles)

    text = (
        f"*ТВОЙ ТИП ТЕНИ*\n\n"
        f"{main_type_name}\n\n"
        f"{type_description}\n\n"
        f"━━━━━━━━━━━━━━\n\n"
        f"*ПРОФИЛЬ ТЕНИ*\n"
        f"{profile_block}\n\n"
        f"━━━━━━━━━━━━━━\n\n"
        f"*ВТОРОЙ СЛОЙ ТЕНИ*\n\n"
        f"{second_type_name}\n\n"
        f"━━━━━━━━━━━━━━\n\n"
        f"У каждого человека есть Тень.\n"
        f"Иногда она проявляется там, где мы её совсем не ждём.\n\n"
        f"Проверь свой результат и сравни с друзьями."
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
        "Этот тест помогает увидеть скрытые психологические паттерны и реакции, "
        "которые обычно остаются вне внимания.\n\n"
        "*Как отвечать:*\n"
        "Читайте вопрос и выбирайте тот вариант, который ближе всего вам.\n\n"
        "Здесь нет правильных или неправильных ответов.\n"
        "Важно отвечать честно и не пытаться выбирать «идеальные» варианты."
    ),
    "questions": questions,
    "get_option_text": lambda option: option["text"],
    "get_option_value": lambda option: option["value"],
    "build_result": build_result,
}
