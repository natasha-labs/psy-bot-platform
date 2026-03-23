import random

PATTERN_RU = {
    "control": "контроль",
    "avoid": "уход",
    "react": "реакция",
    "analyze": "анализ",
}

CBT_THOUGHT = {
    "control": "если не проконтролирую — плохо",
    "avoid": "лучше не лезть",
    "react": "надо сразу",
    "analyze": "надо всё обдумать",
}

DISTORTION = {
    "control": "гиперконтроль",
    "avoid": "избегание",
    "react": "импульс",
    "analyze": "зацикливание",
}

MANIFESTATIONS = {
    "control": ["держишь внутри", "не проговариваешь", "перегружаешься"],
    "avoid": ["откладываешь решения", "уходишь", "не проговариваешь"],
    "react": ["всплески", "перегружаешься", "не проговариваешь"],
    "analyze": ["возвращаешься к мыслям", "перегружаешься", "откладываешь решения"],
}


def build_deep_result(main_pattern, second_pattern, archetype):
    def block1():
        variants = [
            f"Ты используешь стратегию — {PATTERN_RU[main_pattern]}. Это создаёт повторяющийся цикл.",
            f"В напряжении включается {PATTERN_RU[main_pattern]}, и ситуация не решается."
        ]
        return random.choice(variants)

    def block2():
        return f"Снаружи ты — {archetype}, внутри — {PATTERN_RU[second_pattern]}."

    def block3():
        items = MANIFESTATIONS[main_pattern][:3]
        return "\n".join([f"— {i}" for i in items])

    def block4():
        return f"{CBT_THOUGHT[main_pattern]}\nИскажение: {DISTORTION[main_pattern]}"

    def block5():
        return "Твоя точка — момент до реакции. У тебя есть 1–3 секунды."

    def block6():
        return f"Сегодня заметишь → {PATTERN_RU[main_pattern]}"

    def block7():
        return "Это сценарий. И ты его увидел."

    return {
        "part1": f"{block1()}\n\n{block2()}",
        "part2": f"{block3()}\n\n{block4()}",
        "part3": f"{block5()}\n\n{block6()}\n\n{block7()}",
    }
