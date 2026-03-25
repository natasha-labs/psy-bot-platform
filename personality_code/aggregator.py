def enough_for_basic_personality_code(results: dict) -> bool:
    return all(key in results for key in ("anxiety", "archetype", "shadow"))


def build_basic_personality_code(results: dict) -> dict:
    archetype_payload = results.get("archetype", {}).get("profile_payload", {}) or {}
    shadow_payload = results.get("shadow", {}).get("profile_payload", {}) or {}
    anxiety_payload = results.get("anxiety", {}).get("profile_payload", {}) or {}

    main_label = (
        archetype_payload.get("main_label")
        or archetype_payload.get("main_type")
        or archetype_payload.get("archetype_label")
        or archetype_payload.get("archetype_type")
        or "—"
    )

    hidden_label = (
        shadow_payload.get("hidden_label")
        or shadow_payload.get("hidden_type")
        or shadow_payload.get("main_label")
        or shadow_payload.get("main_type")
        or shadow_payload.get("shadow_label")
        or shadow_payload.get("shadow_type")
        or "—"
    )

    current_label = (
        anxiety_payload.get("current_label")
        or anxiety_payload.get("current_state")
        or anxiety_payload.get("main_label")
        or anxiety_payload.get("main_type")
        or anxiety_payload.get("anxiety_label")
        or anxiety_payload.get("anxiety_type")
        or "—"
    )

    if isinstance(current_label, str) and current_label.strip().lower() == "высокий":
        current_label = "Высокий уровень внутреннего напряжения"
    elif isinstance(current_label, str) and current_label.strip().lower() == "средний":
        current_label = "Средний уровень внутреннего напряжения"
    elif isinstance(current_label, str) and current_label.strip().lower() == "низкий":
        current_label = "Низкий уровень внутреннего напряжения"

    return {
        "main_label": main_label,
        "hidden_label": hidden_label,
        "current_label": current_label,
    }
