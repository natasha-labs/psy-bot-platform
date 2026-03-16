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


def ensure_user_record(user_id):
    data = load_results()
    user_id = str(user_id)

    if user_id not in data:
        data[user_id] = {
            "access_level": "free",
            "tests": {},
            "personality_code_version": None,
            "last_personality_code_payload": None,
        }
        save_results(data)

    else:
        changed = False

        if "access_level" not in data[user_id]:
            data[user_id]["access_level"] = "free"
            changed = True

        if "tests" not in data[user_id]:
            data[user_id]["tests"] = {}
            changed = True

        if "personality_code_version" not in data[user_id]:
            data[user_id]["personality_code_version"] = None
            changed = True

        if "last_personality_code_payload" not in data[user_id]:
            data[user_id]["last_personality_code_payload"] = None
            changed = True

        if changed:
            save_results(data)

    return data


def save_user_result(user_id, test_key, title, result_text, profile_payload=None):
    data = ensure_user_record(user_id)
    user_id = str(user_id)

    data[user_id]["tests"][test_key] = {
        "title": title,
        "result_text": result_text,
        "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "profile_payload": profile_payload,
    }

    save_results(data)


def get_user_results(user_id):
    data = ensure_user_record(user_id)
    return data.get(str(user_id), {}).get("tests", {})


def get_user_access_level(user_id):
    data = ensure_user_record(user_id)
    return data.get(str(user_id), {}).get("access_level", "free")


def set_user_access_level(user_id, access_level):
    data = ensure_user_record(user_id)
    user_id = str(user_id)
    data[user_id]["access_level"] = access_level
    save_results(data)


def save_personality_code_payload(user_id, payload, version="basic_v1"):
    data = ensure_user_record(user_id)
    user_id = str(user_id)

    data[user_id]["personality_code_version"] = version
    data[user_id]["last_personality_code_payload"] = payload

    save_results(data)


def get_personality_code_payload(user_id):
    data = ensure_user_record(user_id)
    user_id = str(user_id)
    return data.get(user_id, {}).get("last_personality_code_payload")


def delete_user_results(user_id):
    data = load_results()
    user_id = str(user_id)

    if user_id in data:
        del data[user_id]
        save_results(data)
        return True

    return False
