def enough_for_basic_personality_code(results: dict) -> bool:
    required = {"anxiety", "archetype", "shadow"}
    return required.issubset(set(results.keys()))


def build_basic_personality_code(results: dict) -> dict:
    archetype = results["archetype"].get("profile_payload", {})
    shadow = results["shadow"].get("profile_payload", {})
    anxiety = results["anxiety"].get("profile_payload", {})

    archetype_main = archetype.get("main_label", "")
    shadow_main = shadow.get("main_label", "")
    current_state = anxiety.get("main_label", "")

    synthesis = (
        f"Снаружи вы чаще проявляетесь через тип «{archetype_main}», "
        f"но внутри может включаться тема «{shadow_main.lower()}».\n\n"
        f"Сейчас это усиливается состоянием «{current_state.lower()}»."
    )

    return {
        "archetype_main": archetype_main,
        "shadow_main": shadow_main,
        "current_state": current_state,
        "synthesis": synthesis,
    }
