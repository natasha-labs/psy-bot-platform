PRIMARY_PORTRAIT = {
    "CONTROL": (
        "Ты склонен(а) брать ситуацию под контроль, особенно когда появляется неопределённость. "
        "Тебе важно понимать, что происходит, и удерживать ощущение управляемости."
    ),
    "AVOIDANCE": (
        "Ты стремишься сохранять внутреннюю стабильность, избегая ситуаций, которые могут вызвать напряжение или перегрузку."
    ),
    "REACTION": (
        "Ты быстро реагируешь на происходящее, и твои эмоции включаются раньше, чем появляется возможность их обдумать."
    ),
    "SUPPRESSION": (
        "Ты стараешься держать всё внутри и не показывать, что происходит на самом деле, даже когда напряжение уже накопилось."
    ),
}

PRIMARY_RU = {
    "CONTROL": "контроль",
    "AVOIDANCE": "избегание",
    "REACTION": "реакция",
    "SUPPRESSION": "сдерживание",
}

HOW_IT_WORKS = {
    "CONTROL": (
        "Контроль для тебя — это не просто привычка, а способ справляться с внутренним напряжением. "
        "Когда ситуация становится непонятной, ты усиливаешь контроль, чтобы вернуть ощущение опоры."
    ),
    "AVOIDANCE": (
        "Избегание для тебя — это способ не входить в состояние перегрузки. "
        "Ты выбираешь отойти, отложить или переключиться, чтобы сохранить внутреннее равновесие."
    ),
    "REACTION": (
        "Реакция для тебя — это быстрый способ сбросить напряжение. "
        "Ты не всегда успеваешь осмыслить происходящее до того, как включается ответ."
    ),
    "SUPPRESSION": (
        "Сдерживание для тебя — это способ сохранить стабильность. "
        "Ты удерживаешь эмоции внутри, чтобы не разрушить ситуацию или не показать уязвимость."
    ),
}

BLIND_SPOT = {
    "CONTROL": (
        "Ты можешь считать, что твоя сила — в ответственности и умении держать всё под контролем. "
        "Но на деле это способ снизить внутреннюю тревогу через управление внешним."
    ),
    "AVOIDANCE": (
        "Ты можешь считать, что просто не хочешь лишнего напряжения. "
        "Но на деле ты уходишь от ситуаций, которые требуют внутреннего усилия."
    ),
    "REACTION": (
        "Ты можешь считать, что просто честно реагируешь. "
        "Но на деле реакция возникает быстрее, чем понимание, и это управляет твоим поведением."
    ),
    "SUPPRESSION": (
        "Ты можешь считать, что хорошо держишь себя в руках. "
        "Но на деле ты накапливаешь напряжение, которое позже всё равно выходит."
    ),
}

MECHANISM_TEXT = (
    "Когда ситуация становится напряжённой → включается внутреннее напряжение → "
    "ты используешь свой основной способ поведения → это даёт временный эффект → "
    "но не решает причину → напряжение возвращается."
)

IN_THE_MOMENT = {
    "FREEZE": (
        "В момент напряжения ты не переходишь к действию, а скорее замираешь и уходишь внутрь себя. "
        "Снаружи это может выглядеть как спокойствие, но внутри происходит сильная нагрузка."
    ),
    "ESCAPE": (
        "Ты стараешься отойти от ситуации — переключиться, отложить или избежать прямого контакта. "
        "Это даёт краткое облегчение, но оставляет ситуацию нерешённой."
    ),
    "OUTBURST": (
        "Реакция возникает резко и быстро. Сначала происходит всплеск, и только потом приходит осмысление."
    ),
    "OVERCONTROL": (
        "Ты усиливаешь контроль ещё больше — пытаешься удержать детали, просчитать и стабилизировать ситуацию."
    ),
    "PEOPLE_PLEASING": (
        "Ты подстраиваешься под других, чтобы сохранить контакт и избежать конфликта, даже если внутри есть напряжение."
    ),
}

ENERGY_PRIMARY = {
    "CONTROL": "Энергия уходит на постоянное удержание ситуации и попытку всё контролировать.",
    "AVOIDANCE": "Энергия уходит на избегание и возвращение к одним и тем же ситуациям.",
    "REACTION": "Энергия уходит на всплески и восстановление после них.",
    "SUPPRESSION": "Энергия уходит на удержание эмоций внутри.",
}

ENERGY_BEHAVIOR = {
    "FREEZE": "уходишь в себя и проживаешь всё внутри",
    "ESCAPE": "откладываешь и уходишь от прямого контакта",
    "OUTBURST": "реагируешь резко и импульсивно",
    "OVERCONTROL": "усиливаешь контроль и пытаешься удержать всё",
    "PEOPLE_PLEASING": "подстраиваешься под других и сглаживаешь ситуацию",
}

WHAT_TO_DO = {
    "CONTROL": "Отслеживай момент, когда ты усиливаешь контроль — это сигнал напряжения, а не реальной необходимости.",
    "AVOIDANCE": "Замечай, где ты откладываешь или уходишь, и возвращайся к этим точкам осознанно.",
    "REACTION": "Давай себе паузу перед реакцией — даже короткая задержка меняет поведение.",
    "SUPPRESSION": "Начни фиксировать свои состояния, а не только удерживать их внутри.",
}

COMMON_ENDING = (
    "Разделяй: где действительно нужна реакция, а где ты просто пытаешься справиться с внутренним напряжением."
)


def _secondary_text(secondary_pattern: str) -> str:
    return PRIMARY_RU.get(secondary_pattern, secondary_pattern)


def build_portrait(primary_pattern: str, secondary_pattern: str) -> str:
    text = PRIMARY_PORTRAIT[primary_pattern]
    if secondary_pattern:
        text += (
            f"\nДополнительно в тебе проявляется {_secondary_text(secondary_pattern)}, "
            "и это усиливает общий паттерн поведения."
        )
    return text


def build_how_it_works(primary_pattern: str) -> str:
    return HOW_IT_WORKS[primary_pattern]


def build_blind_spot(primary_pattern: str) -> str:
    return BLIND_SPOT[primary_pattern]


def build_mechanism() -> str:
    return MECHANISM_TEXT


def build_in_the_moment(behavior_modifier: str) -> str:
    return IN_THE_MOMENT[behavior_modifier]


def build_conflict(archetype_type: str, shadow_type: str) -> str:
    return (
        f"С одной стороны ты стремишься к {archetype_type}. "
        f"С другой — внутри есть {shadow_type}, который ограничивает это. "
        "Это создаёт внутреннее напряжение и ощущение, что ты не можешь реализовать себя так, как чувствуешь."
    )


def build_energy(primary_pattern: str, behavior_modifier: str) -> str:
    first = ENERGY_PRIMARY[primary_pattern]
    second = (
        f"И это усиливается тем, что ты {ENERGY_BEHAVIOR[behavior_modifier]}, "
        "из-за чего этот цикл повторяется."
    )
    return f"{first}\n{second}"


def build_actions(primary_pattern: str) -> str:
    return f"{WHAT_TO_DO[primary_pattern]}\n{COMMON_ENDING}"


def build_deep_result(
    archetype_type: str,
    shadow_type: str,
    anxiety_type: str,
    primary_pattern: str,
    secondary_pattern: str,
    behavior_modifier: str,
) -> dict:
    blocks = [
        build_portrait(primary_pattern, secondary_pattern),
        build_how_it_works(primary_pattern),
        build_blind_spot(primary_pattern),
        build_mechanism(),
        build_in_the_moment(behavior_modifier),
        build_conflict(archetype_type, shadow_type),
        build_energy(primary_pattern, behavior_modifier),
        build_actions(primary_pattern),
    ]

    full_text = "\n\n".join(blocks)

    return {
        "text": full_text,
        "share_text": "Я прошёл глубокий разбор личности",
        "primary_pattern": primary_pattern,
        "secondary_pattern": secondary_pattern,
        "behavior_modifier": behavior_modifier,
    }
