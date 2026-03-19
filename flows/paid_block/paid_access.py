from storage.results_store import has_paid_access as storage_has_paid_access
from storage.results_store import set_paid_access


def has_paid_access(user_id) -> bool:
    return storage_has_paid_access(user_id)


def grant_paid_access(user_id) -> None:
    set_paid_access(user_id, True)


def revoke_paid_access(user_id) -> None:
    set_paid_access(user_id, False)
