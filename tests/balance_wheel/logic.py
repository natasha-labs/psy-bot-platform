def find_main_problem(data: dict):
    candidates = []

    for sphere, values in data.items():
        importance = values["importance"]
        satisfaction = values["satisfaction"]
        action = values["action"]

        priority = False

        if importance >= 4 and satisfaction <= 2 and action == 1:
            priority = True

        if importance >= 4 and satisfaction == 3:
            priority = True

        candidates.append({
            "sphere": sphere,
            "importance": importance,
            "satisfaction": satisfaction,
            "action": action,
            "priority": priority
        })

    priority_list = [c for c in candidates if c["priority"]]

    if priority_list:
        priority_list.sort(
            key=lambda x: (-x["importance"], x["satisfaction"], x["action"])
        )
        return priority_list[0]["sphere"]

    # fallback
    candidates.sort(
        key=lambda x: (-x["importance"], x["satisfaction"], x["action"])
    )
    return candidates[0]["sphere"]
