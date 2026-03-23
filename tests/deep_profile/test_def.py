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


def build_result(user_id, answers):

    scores = {
        "control": 0,
        "avoid": 0,
        "react": 0,
        "analyze": 0,
    }

    for answer in answers:
        for key, value in answer.items():
            scores[key] += value

    main_pattern, second_pattern = resolve_patterns(scores)

    profile = get_user_profile(user_id)
    archetype = profile.get("archetype_type", "—")

    return build_deep_result(
        main_pattern,
        second_pattern,
        archetype
    )
