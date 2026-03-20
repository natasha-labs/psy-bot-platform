from storage.results_store import (
    has_paid_access as storage_has_paid_access,
    set_paid_access,
    mark_deep_profile_started,
    mark_deep_profile_completed,
)


def has_paid_access(user_id) -> bool:
    return storage_has_paid_access(user_id)


def grant_paid_access(user_id) -> None:
    set_paid_access(user_id, True)


def revoke_paid_access(user_id) -> None:
    set_paid_access(user_id, False)
    mark_deep_profile_started(user_id, False)
    mark_deep_profile_completed(user_id, False)
