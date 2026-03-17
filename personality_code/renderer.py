def render_basic_personality_code(payload):
    sections = payload.get("sections", {})

    identity = sections.get("identity_core", {})
    shadow = sections.get("shadow_layer", {})
    stress = sections.get("stress_modifier", {})
    reaction_style = sections.get("reaction_style", "")
    inner_conflict = sections.get("inner_conflict", "")
    growth_vector = sections.get("growth_vector", "")
    risk_pattern = sections.get("risk_pattern", "")

    lines = [
        "✨ *КОД ЛИЧНОСТИ*",
        "Ваш психологический профиль",
        "",
        "━━━━━━━━━━━━━━",
        "",
        "*Кто вы в основе*",
        f"Ваше ядро сейчас проявляется через тип «{identity.get('main_label', '')}».",
        identity.get("summary", ""),
        "",
        "━━━━━━━━━━━━━━",
        "",
        "*Что в вас скрыто*",
        f"В тени сильнее всего звучит тема «{shadow.get('main_label', '')}».",
        shadow.get("summary", ""),
        "",
        "━━━━━━━━━━━━━━",
        "",
        "*Что сейчас влияет на ваши реакции*",
        f"Текущий фактор напряжения — «{stress.get('main_label', '')}».",
        stress.get("summary", ""),
        "",
        "━━━━━━━━━━━━━━",
        "",
        "*Как это соединяется в одну картину*",
        reaction_style,
        "",
        "*Точка внутреннего конфликта*",
        inner_conflict,
        "",
        "*Вектор роста*",
        growth_vector,
        "",
        "*Риск перекоса*",
        risk_pattern,
    ]

    return "\n".join(line for line in lines if line is not None)


def render_basic_code_ready_text():
    return (
        "✨ *Ваш базовый код личности готов*\n\n"
        "На основе трёх тестов мы собрали\n"
        "ваш начальный психологический профиль.\n\n"
        "Он показывает:\n\n"
        "• как вы проявляетесь в мире\n"
        "• какие реакции скрыты\n"
        "• что влияет на ваши решения"
    )


def render_upsell_text():
    return (
        "🧠 *ЭТО ТОЛЬКО ПЕРВЫЙ СЛОЙ*\n\n"
        "Базовый код личности показывает основу.\n\n"
        "Но реальный психологический профиль человека\n"
        "намного глубже.\n\n"
        "Полная система «Код личности» раскрывает:\n\n"
        "💔 ваш сценарий любви\n"
        "почему вы выбираете определённых партнёров\n\n"
        "🧒 внутреннего ребёнка\n"
        "какие детские реакции до сих пор управляют решениями\n\n"
        "🔥 страх близости\n"
        "что мешает вам строить глубокие отношения\n\n"
        "🛡 скрытые защитные механизмы психики\n"
        "как ваша психика защищает вас от боли\n\n"
        "👑 систему 12 архетипов личности\n"
        "глубокую архетипическую структуру по Карлу Юнгу"
    )
