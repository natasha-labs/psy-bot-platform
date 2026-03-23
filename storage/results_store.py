import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
RESULTS_FILE = BASE_DIR / "user_results.json"


def _ensure_file():
    if not RESULTS_FILE.exists():
        RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)
        RESULTS_FILE.write_text("{}", encoding="utf-8")


def load_results():
    _ensure_file()
    try:
        return json.loads(RESULTS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_results(data):
    RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    RESULTS_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def ensure_user_profile(user_id):
    data = load_results()
    user_id = str(user_id)

    if user_id not in data:
        data[user_id] = {
            "user_id": int(user_id) if str(user_id).isdigit() else user_id,
            "completed_tests": [],
            "results": {},
            "paid_access": False,
            "deep_profile_started": False,
            "deep_profile_completed": False,
            "deep_profile_result": None,
            "primary_pattern": None,
            "secondary_pattern": None,
            "behavior_modifier": None,
            "deep_profile_answers": [],
            "deep_profile_signals": {},
            "deep_profile_completed_at": None,
            "archetype_type": None,
            "shadow_type": None,
            "anxiety_type": None,
            "payment_info": None,
        }
        save_results(data)

    return data


def save_user_result(user_id, test_key, title, result_text, profile_payload=None):
    data = ensure_user_profile(user_id)
    user_id = str(user_id)
    profile_payload = profile_payload or {}

    data[user_id]["results"][test_key] = {
        "title": title,
        "result_text": result_text,
        "profile_payload": profile_payload,
        "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }

    completed = set(data[user_id].get("completed_tests", []))
    completed.add(test_key)
    data[user_id]["completed_tests"] = list(completed)

    if test_key == "archetype":
        data[user_id]["archetype_type"] = profile_payload.get("main_label") or profile_payload.get("main_type")
    elif test_key == "shadow":
        data[user_id]["shadow_type"] = profile_payload.get("main_label") or profile_payload.get("main_type")
    elif test_key == "anxiety":
        data[user_id]["anxiety_type"] = profile_payload.get("main_label") or profile_payload.get("main_type")

    save_results(data)


def get_user_results(user_id):
    data = ensure_user_profile(user_id)
    return data.get(str(user_id), {}).get("results", {})


def get_user_profile(user_id):
    data = ensure_user_profile(user_id)
    return data.get(str(user_id), {})


def get_completed_tests(user_id):
    return get_user_profile(user_id).get("completed_tests", [])


def delete_user_results(user_id):
    data = load_results()
    user_id = str(user_id)

    if user_id in data:
        del data[user_id]
        save_results(data)
        return True

    return False


def set_paid_access(user_id, value: bool):
    data = ensure_user_profile(user_id)
    user_id = str(user_id)
    data[user_id]["paid_access"] = bool(value)
    save_results(data)


def has_paid_access(user_id) -> bool:
    profile = get_user_profile(user_id)
    return bool(profile.get("paid_access", False))


def mark_deep_profile_started(user_id, value=True):
    data = ensure_user_profile(user_id)
    user_id = str(user_id)
    data[user_id]["deep_profile_started"] = bool(value)
    save_results(data)


def mark_deep_profile_completed(user_id, value=True):
    data = ensure_user_profile(user_id)
    user_id = str(user_id)
    data[user_id]["deep_profile_completed"] = bool(value)
    save_results(data)


def set_payment_info(user_id, payment_info: dict):
    data = ensure_user_profile(user_id)
    user_id = str(user_id)
    data[user_id]["payment_info"] = payment_info
    save_results(data)


def save_deep_profile_result(
    user_id,
    result_payload,
    answers,
    signal_map,
    primary_pattern,
    secondary_pattern,
    behavior_modifier=None,
):
    data = ensure_user_profile(user_id)
    user_id = str(user_id)

    data[user_id]["deep_profile_result"] = "\n\n".join(
        [
            result_payload.get("part1", ""),
            result_payload.get("part2", ""),
            result_payload.get("part3", ""),
        ]
    ).strip()
    data[user_id]["primary_pattern"] = primary_pattern
    data[user_id]["secondary_pattern"] = secondary_pattern
    data[user_id]["behavior_modifier"] = behavior_modifier
    data[user_id]["deep_profile_answers"] = answers
    data[user_id]["deep_profile_signals"] = signal_map
    data[user_id]["deep_profile_completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    data[user_id]["deep_profile_started"] = True
    data[user_id]["deep_profile_completed"] = True

    completed = set(data[user_id].get("completed_tests", []))
    completed.add("deep_profile")
    data[user_id]["completed_tests"] = list(completed)

    save_results(data)
