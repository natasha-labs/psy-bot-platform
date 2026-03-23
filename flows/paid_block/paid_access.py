from storage.results_store import set_paid_access, has_paid_access

def grant_paid_access(user_id):
    set_paid_access(user_id, True)

def check_access(user_id):
    return has_paid_access(user_id)
