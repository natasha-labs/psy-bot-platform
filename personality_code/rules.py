def build_reaction_style(sections):
    archetype = sections.get("identity_core")
    shadow = sections.get("shadow_layer")
    anxiety = sections.get("stress_modifier")

    if not archetype or not shadow or not anxiety:
        return "Недостаточно данных для построения стиля реакции."

    return (
        f"Снаружи вы чаще проявляетесь через архетип «{archetype['main_label']}», "
        f"но внутри вами может управлять теневая тема «{shadow['main_label']}». "
        f"Текущий уровень напряжения — «{anxiety['main_label']}», и он влияет на то, "
        f"насколько свободно вам сейчас доступна ваша естественная сила."
    )


def build_inner_conflict(sections):
    archetype = sections.get("identity_core")
    shadow = sections.get("shadow_layer")

    if not archetype or not shadow:
        return "Недостаточно данных для построения внутреннего конфликта."

    return (
        f"Ваш внутренний конфликт может проявляться между способом жить как «{archetype['main_label']}» "
        f"и скрытой защитой по типу «{shadow['main_label']}». "
        f"То есть одна часть вас хочет проявляться естественно, а другая — старается защитить от уязвимости или перегруза."
    )


def build_growth_vector(sections):
    growth_points = []

    for section in sections.values():
        point = section.get("growth_point")
        if point:
            growth_points.append(point)

    if not growth_points:
        return "Точка роста будет доступна после прохождения тестов."

    return " ".join(growth_points[:3])


def build_risk_pattern(sections):
    risk_blocks = []

    for section in sections.values():
        risk = section.get("risk_zone")
        if risk:
            risk_blocks.append(risk)

    if not risk_blocks:
        return "Риск перекоса будет доступен после прохождения тестов."

    return " ".join(risk_blocks[:3])
