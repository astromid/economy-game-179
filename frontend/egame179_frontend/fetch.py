import time
from collections.abc import Callable
from functools import wraps
from typing import Any

import streamlit as st
from streamlit_server_state import server_state, server_state_lock

from egame179_frontend import api as egame179_api
from egame179_frontend.state import SharedGameState


def fetch_spinner(stage: int | None = None, total: int | None = None) -> Callable:
    """Fetch data spinner decorator.

    Args:
        stage (int, optional): stage number. Defaults to None.
        total (int, optional): total stages. Defaults to None.

    Returns:
        Callable: decorator.
    """

    def decorator(func: Callable) -> Callable[[], Any]:
        @wraps(func)
        def wrapper() -> Any:
            msg = "Синхронизация данных..."
            if stage is not None:
                if total is not None:
                    msg = f"{msg} [{stage}/{total}]"
                else:
                    msg = f"{msg} [{stage}]"
            with st.spinner(msg):
                return func()

        return wrapper

    return decorator





def fetch_shared_state() -> SharedGameState:
    return SharedGameState(
        synced=True,
        cycle=fetch_current_cycle(),
        markets=[],
    )


@fetch_spinner(stage=1, total=4)
def fetch_current_cycle() -> egame179_api.models.Cycle:
    time.sleep(5)  # !DEBUG
    return egame179_api.CycleAPI.get_current_cycle()
