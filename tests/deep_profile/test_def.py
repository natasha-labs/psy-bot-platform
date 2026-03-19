from tests.deep_profile.questions import questions
from storage.results_store import get_user_profile
from flows.paid_block.deep_result_builder import build_deep_result


TEST_DEF = {
    "key": "deep_profile",
    "title": "Глубокий профиль",
    "intro_text": "Сейчас мы уточним ваш профиль через дополнительные вопросы.",
    "questions": questions,
}


def get_option_text(option):
    return option["text"]


def get_option_value(option):
    return option["value"]


def build_result(user_id, answers):
    signals = {
        "CONTROL": 0,
        "AVOIDANCE": 0,
        "REACTION": 0,
        "SUPPRESSION": 0,
    }

    for answer in answers:
        value = answer.get("value", {})
        for key, score in value.items():
            signals[key] += score

    sorted_signals = sorted(signals.items(), key=lambda x: x[1], reverse=True)

    primary_pattern = sorted_signals[0][0]
    secondary_pattern = sorted_signals[1][0]

    profile = get_user_profile(user_id)

    archetype = profile.get("archetype_type")
    shadow = profile.get("shadow_type")
    anxiety = profile.get("anxiety_type")

    result = build_deep_result(
        archetype,
        shadow,
        anxiety,
        primary_pattern,
        secondary_pattern,
    )

    result["signals"] = signals
    result["archetype_type"] = archetype
    result["shadow_type"] = shadow
    result["anxiety_type"] = anxiety

    return result
