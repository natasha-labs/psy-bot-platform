import tempfile


def generate_wheel(data: dict) -> str:
    text = "Колесо баланса:\n\n"

    for k, v in data.items():
        text += f"{k}: {v}\n"

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
    path = temp_file.name

    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

    return path
