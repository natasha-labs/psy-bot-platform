from storage.results_store import get_user_profile


def enough_for_basic_personality_code(results: dict) -> bool:
    required = {"anxiety", "archetype", "shadow"}
    return required.issubset(set(results.keys()))


def build_basic_personality_code(results: dict, user_id=None) -> dict:
    profile = get_user_profile(user_id) if user_id is not None else {}

    archetype_type = profile.get("archetype_type")
    shadow_type = profile.get("shadow_type")
    anxiety_type = profile.get("anxiety_type")

    if not archetype_type and "archetype" in results:
        archetype_type = (
            results["archetype"].get("profile_payload", {}).get("main_label")
            or results["archetype"].get("profile_payload", {}).get("main_type")
        )

    if not shadow_type and "shadow" in results:
        shadow_type = (
            results["shadow"].get("profile_payload", {}).get("main_label")
            or results["shadow"].get("profile_payload", {}).get("main_type")
        )

    if not anxiety_type and "anxiety" in results:
        anxiety_type = (
            results["anxiety"].get("profile_payload", {}).get("main_label")
            or results["anxiety"].get("profile_payload", {}).get("main_type")
        )

    return {
        "main_type": archetype_type or "—",
        "shadow_type": shadow_type or "—",
        "anxiety_type": anxiety_type or "—",
    }
