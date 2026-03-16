from personality_code.registry import BASIC_REQUIRED_TESTS, TEST_ROLES
from personality_code.rules import (
    build_reaction_style,
    build_inner_conflict,
    build_growth_vector,
    build_risk_pattern,
)


def collect_completed_test_payloads(user_tests: dict):
    collected = {}

    for test_key, item in user_tests.items():
        payload = item.get("profile_payload")
        if payload:
            collected[test_key] = payload

    return collected


def enough_for_basic_personality_code(user_tests: dict) -> bool:
    collected = collect_completed_test_payloads(user_tests)
    completed_keys = set(collected.keys())
    return all(test_key in completed_keys for test_key in BASIC_REQUIRED_TESTS)


def build_sections(collected_payloads: dict):
    sections = {}

    for test_key, payload in collected_payloads.items():
        role = TEST_ROLES.get(test_key)
        if role:
            sections[role] = payload

    return sections


def build_basic_personality_code(user_tests: dict):
    collected_payloads = collect_completed_test_payloads(user_tests)
    completed_tests = list(collected_payloads.keys())
    enough = enough_for_basic_personality_code(user_tests)
    sections = build_sections(collected_payloads)

    reaction_style = build_reaction_style(sections)
    inner_conflict = build_inner_conflict(sections)
    growth_vector = build_growth_vector(sections)
    risk_pattern = build_risk_pattern(sections)

    return {
        "completed_tests": completed_tests,
        "enough_for_personality_code": enough,
        "sections": {
            **sections,
            "reaction_style": reaction_style,
            "inner_conflict": inner_conflict,
            "growth_vector": growth_vector,
            "risk_pattern": risk_pattern,
        },
        "summary_title": "Код личности",
        "summary_subtitle": "Ваш личный психологический профиль",
    }
