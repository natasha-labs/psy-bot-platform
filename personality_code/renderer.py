from telegram import InlineKeyboardMarkup, InlineKeyboardButton


def _pick(payload: dict, *keys, default="—"):
    for key in keys:
        value = payload.get(key)
        if value:
            return value
    return default


def _normalize_anxiety_label(value: str) -> str:
    mapping = {
        "Низкий": "Низкий уровень внутреннего напряжения",
        "Умеренный": "Умеренный уровень внутреннего напряжения",
        "Высокий": "Высокий уровень внутреннего напряжения",
        "Очень высокий": "Очень высокий уровень внутреннего напряжения",
        "низкий": "Низкий уровень внутреннего напряжения",
        "умеренный": "Умеренный уровень внутреннего напряжения",
        "высокий": "Высокий уровень внутреннего напряжения",
        "очень высокий": "Очень высокий уровень внутреннего напряжения",
    }
    return mapping.get(value, value or "—")


def _build_summary(main_type: str, shadow_type: str, anxiety_label: str) -> str:
    return (
        "✨ *Ваш базовый код личности*\n\n"
        f"🔹 Кто вы в основе — *{main_type}*\n"
        f"🔹 Что скрыто — *{shadow_type}*\n"
        f"🔹 Что влияет сейчас — *{anxiety_label}*"
    )


def _build_interpretation(main_type: str, shadow_type: str, anxiety_label: str) -> str:
    return (
        f"Снаружи вы чаще проявляетесь через тип *«{main_type}»*.\n"
        f"Но внутри может включаться тема *«{shadow_type}»*, "
        "из-за которой реакции становятся более жёсткими, тревожными или закрытыми.\n\n"
        f"Сейчас это усиливается состоянием *«{anxiety_label}»*.\n"
        "Именно поэтому часть решений может приниматься не из спокойствия, а из внутреннего напряжения."
    )


def _build_value_block() -> str:
    return (
        "Полный разбор покажет:\n\n"
        "— почему вы выбираете определённых партнёров\n"
        "— какие реакции управляют вами\n"
        "— где вы теряете энергию\n"
        "— как это изменить"
    )


def render_basic_personality_code(payload: dict) -> str:
    main_type = _pick(payload, "main_type", "archetype_type", "archetype_main")
    shadow_type = _pick(payload, "shadow_type", "archetype_shadow")
    anxiety_raw = _pick(payload, "anxiety_type", "current_state", "state_type")
    anxiety_label = _normalize_anxiety_label(anxiety_raw)

    parts = [
        _build_summary(main_type, shadow_type, anxiety_label),
        _build_interpretation(main_type, shadow_type, anxiety_label),
        _build_value_block(),
    ]

    return "\n\n".join(parts)


def render_full_profile_stub_text():
    return (
        "🔒 *Полный разбор личности*\n\n"
        "Глубокая версия подключается через платный второй этап."
    )


def render_full_profile_stub_keyboard():
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("Разобрать глубже", callback_data="full_profile_info")]]
    )
