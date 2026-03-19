SIGNAL_LABELS = {
    "CONTROL": "Контроль",
    "AVOIDANCE": "Избегание",
    "REACTION": "Реактивность",
    "SUPPRESSION": "Подавление",
}


def sort_signals(signal_map: dict) -> list[tuple[str, int]]:
    return sorted(signal_map.items(), key=lambda item: item[1], reverse=True)


def build_thinking_section(archetype_type: str, primary_pattern: str) -> str:
    return (
        f"Как думает:\n"
        f"Основа — {archetype_type or '—'}.\n"
        f"Ведущий паттерн — {SIGNAL_LABELS.get(primary_pattern, primary_pattern)}."
    )


def build_decision_section(anxiety_type: str, primary_pattern: str, secondary_pattern: str) -> str:
    return (
        f"Как принимает решения:\n"
        f"Тревожный профиль — {anxiety_type or '—'}.\n"
        f"Ведущие сигналы — "
        f"{SIGNAL_LABELS.get(primary_pattern, primary_pattern)} / "
        f"{SIGNAL_LABELS.get(secondary_pattern, secondary_pattern)}."
    )


def build_distortion_section(shadow_type: str, primary_pattern: str, secondary_pattern: str) -> str:
    return (
        f"Где искажает реальность:\n"
        f"Теневая тема — {shadow_type or '—'}.\n"
        f"Сигналы — "
        f"{SIGNAL_LABELS.get(primary_pattern, primary_pattern)} / "
        f"{SIGNAL_LABELS.get(secondary_pattern, secondary_pattern)}."
    )


def build_conflict_section(archetype_type: str, shadow_type: str) -> str:
    return (
        f"Где внутренний конфликт:\n"
        f"Архетип — {archetype_type or '—'}.\n"
        f"Тень — {shadow_type or '—'}."
    )


def build_energy_section(primary_pattern: str, secondary_pattern: str) -> str:
    return (
        f"Где теряет энергию:\n"
        f"Основная утечка — {SIGNAL_LABELS.get(primary_pattern, primary_pattern)}.\n"
        f"Вторичная — {SIGNAL_LABELS.get(secondary_pattern, secondary_pattern)}."
    )


def build_deep_result(
    *,
    archetype_type: str,
    shadow_type: str,
    anxiety_type: str,
    primary_pattern: str,
    secondary_pattern: str,
    signal_map: dict,
) -> dict:
    sections = [
        build_thinking_section(archetype_type, primary_pattern),
        build_decision_section(anxiety_type, primary_pattern, secondary_pattern),
        build_distortion_section(shadow_type, primary_pattern, secondary_pattern),
        build_conflict_section(archetype_type, shadow_type),
        build_energy_section(primary_pattern, secondary_pattern),
    ]

    text = (
        "Глубокий профиль\n\n"
        + "\n\n".join(sections)
    )

    return {
        "text": text,
        "share_text": "Глубокий профиль готов.",
        "primary_pattern": primary_pattern,
        "secondary_pattern": secondary_pattern,
        "signals": signal_map,
    }
