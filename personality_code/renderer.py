from telegram import InlineKeyboardMarkup, InlineKeyboardButton


def render_basic_personality_code(payload: dict) -> str:
    sections = payload.get("sections", {})

    identity_core = sections.get("identity_core")
    shadow_layer = sections.get("shadow_layer")
    stress_modifier = sections.get("stress_modifier")

    lines = [
        "✨ *КОД ЛИЧНОСТИ*",
        "*Ваш личный психологический профиль*",
        "",
    ]

    if identity_core:
        lines.extend([
            "*Кто вы в основе*",
            f"Ваше ядро сейчас проявляется через тип «{identity_core['main_label']}».",
            identity_core.get("summary", ""),
            "",
            "━━━━━━━━━━━━━━",
            "",
        ])

    if shadow_layer:
        lines.extend([
            "*Что в вас скрыто*",
            f"В тени сильнее всего звучит тема «{shadow_layer['main_label']}».",
            shadow_layer.get("summary", ""),
            "",
            "━━━━━━━━━━━━━━",
            "",
        ])

    if stress_modifier:
        lines.extend([
            "*Что сейчас искажает проявление*",
            f"Текущий фактор напряжения — «{stress_modifier['main_label']}».",
            stress_modifier.get("summary", ""),
            "",
            "━━━━━━━━━━━━━━",
            "",
        ])

    lines.extend([
        "*Как это соединяется в одну картину*",
        sections.get("reaction_style", ""),
        "",
        "━━━━━━━━━━━━━━",
        "",
        "*Точка внутреннего конфликта*",
        sections.get("inner_conflict", ""),
        "",
        "━━━━━━━━━━━━━━",
        "",
        "*Ваш внутренний риск*",
        sections.get("risk_pattern", ""),
        "",
        "━━━━━━━━━━━━━━",
        "",
        "*Вектор роста*",
        sections.get("growth_vector", ""),
    ])

    return "\n".join(line for line in lines if line is not None)


def render_upsell_text() -> str:
    return (
        "✨ *Ваш базовый код личности готов*\n\n"
        "На основе трёх тестов мы собрали ваш начальный психологический профиль.\n\n"
        "Он показывает:\n"
        "• как вы проявляетесь\n"
        "• какие реакции скрыты\n"
        "• что влияет на ваши решения\n\n"
        "Полный профиль личности раскрывает гораздо больше.\n\n"
        "Он включает дополнительные тесты:\n"
        "• Код любви\n"
        "• Страх близости\n"
        "• Внутренний конфликт\n"
        "• Скрытые защиты психики"
    )


def render_upsell_keyboard():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🔓 Получить полный профиль личности", callback_data="full_profile_info")],
        ]
    )


def render_full_profile_stub_text() -> str:
    return (
        "🔓 *Полный профиль личности*\n\n"
        "Этот уровень скоро появится.\n\n"
        "Здесь будут доступны дополнительные тесты и более глубокий разбор вашей личности."
    )
