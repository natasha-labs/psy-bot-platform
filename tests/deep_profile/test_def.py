from tests.deep_profile.questions import questions
from flows.paid_block.deep_result_builder import build_deep_result
from storage.results_store import get_user_profile

PRIORITY = ["control", "analyze", "avoid", "react"]


def resolve_patterns(scores):
    sorted_items = sorted(
        scores.items(),
        key=lambda x: (-x[1], PRIORITY.index(x[0]))
    )
    return sorted_items[0][0], sorted_items[1][0]


def get_option_text(option):
    return option["text"]


def get_option_value(option):
    return option["value"]


def build_result(user_id, answers):
    scores = {
        "control": 0,
        "avoid": 0,
        "react": 0,
        "analyze": 0,
    }

    for answer in answers:
        value = answer.get("value", {})
        for key, points in value.items():
            if key in scores:
                scores[key] += points

    main_pattern, second_pattern = resolve_patterns(scores)

    profile = get_user_profile(user_id)
    archetype = profile.get("archetype_type", "—")

    result = build_deep_result(
        main_pattern=main_pattern,
        second_pattern=second_pattern,
        archetype=archetype,
    )

    result["scores"] = scores
    result["main_pattern"] = main_pattern
    result["second_pattern"] = second_pattern

    return result


TEST_DEF = {
    "key": "deep_profile",
    "title": "Глубокий профиль",
    "intro_text": "Сейчас мы разберём это глубже.",
    "questions": questions,
    "get_option_text": get_option_text,
    "get_option_value": get_option_value,
    "build_result": build_result,
}
