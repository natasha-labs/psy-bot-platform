def render_basic_personality_code(payload: dict) -> str:
    main_label = (
        payload.get("main_label")
        or payload.get("archetype_label")
        or payload.get("archetype_type")
        or payload.get("main_type")
        or "—"
    )

    hidden_label = (
        payload.get("hidden_label")
        or payload.get("shadow_label")
        or payload.get("shadow_type")
        or payload.get("secondary_label")
        or "—"
    )

    current_label = (
        payload.get("current_label")
        or payload.get("anxiety_label")
        or payload.get("anxiety_type")
        or payload.get("state_label")
        or "—"
    )

    return (
        "✨ *Ваш базовый код личности*\n\n"
        f"🔹 Кто вы в основе — *{main_label}*\n"
        f"🔹 Что скрыто — *{hidden_label}*\n"
        f"🔹 Что влияет сейчас — *{current_label}*\n\n"
        f"Снаружи вы чаще проявляетесь через тип *«{main_label}»*.\n\n"
        f"Скрытый слой связан с темой *«{hidden_label}»*, и именно он может ограничивать, сдерживать или искажать ваши реакции.\n\n"
        f"Сейчас это усиливается состоянием *«{current_label}»*."
    )
