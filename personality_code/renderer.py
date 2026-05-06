def render_basic_personality_code(payload: dict) -> str:
    main_label = payload.get("main_label") or "—"
    hidden_label = payload.get("hidden_label") or "—"
    current_label = payload.get("current_label") or "—"

    return (
        "✨ *Ваш базовый код личности*\n\n"
        f"🔹 В основе вашей реакции — *{main_label}*\n"
        f"🔹 В тени может включаться — *{hidden_label}*\n"
        f"🔹 Сейчас на это влияет — *{current_label}*\n\n"
        f"Снаружи вы чаще проявляетесь через тип *«{main_label}»*.\n\n"
        f"Скрытый слой связан с темой *«{hidden_label}»*, и именно он может ограничивать, сдерживать или искажать ваши реакции.\n\n"
        f"Сейчас это усиливается состоянием *«{current_label}»*."
    )
