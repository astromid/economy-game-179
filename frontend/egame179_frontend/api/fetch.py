from collections.abc import Callable
from typing import Any

from egame179_frontend.api.cycle import get_current_cycle
from egame179_frontend.models import Cycle


def get_fetch_func(user_role: str) -> Callable[[], Any]:
    """Get fetch function.

    Returns:
        Callable: fetch function.

    Raises:
        ValueError: if user role is not supported.
    """
    match user_role:
        case "root":
            return fetch_root_state
    raise ValueError(f"Incorrect user role: {user_role}")


def fetch_root_state() -> Cycle:
    """Fetch root state.

    Returns:
        Cycle: current cycle info.
    """
    return get_current_cycle()
