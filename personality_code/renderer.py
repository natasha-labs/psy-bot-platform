def render_basic_personality_code(payload):
    return (
        "✨ *Ваш базовый код личности*\n\n"
        f"🔹 Кто вы в основе — *{payload['archetype_main']}*\n"
        f"🔹 Что скрыто — *{payload['shadow_main']}*\n"
        f"🔹 Что влияет сейчас — *{payload['current_state']}*\n\n"
        f"{payload['synthesis']}\n\n"
        "Полный разбор покажет:\n\n"
        "— почему вы выбираете определённых партнёров\n"
        "— какие реакции управляют вами\n"
        "— где вы теряете энергию\n"
        "— как это изменить"
    )
