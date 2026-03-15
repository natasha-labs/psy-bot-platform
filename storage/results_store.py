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


def save_user_result(user_id, test_key, title, result_text):
    data = load_results()
    user_id = str(user_id)

    if user_id not in data:
        data[user_id] = {}

    data[user_id][test_key] = {
        "title": title,
        "result_text": result_text,
        "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }

    save_results(data)


def get_user_results(user_id):
    data = load_results()
    return data.get(str(user_id), {})
