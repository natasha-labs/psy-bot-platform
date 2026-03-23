DATA = {}

def get_user_profile(user_id):
    return DATA.get(str(user_id), {})

def set_paid_access(user_id, value):
    uid = str(user_id)
    if uid not in DATA:
        DATA[uid] = {}
    DATA[uid]["paid"] = value

def has_paid_access(user_id):
    return DATA.get(str(user_id), {}).get("paid", False)
