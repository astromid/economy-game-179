from collections.abc import Callable
from functools import wraps
from typing import Any

import streamlit as st


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
            msg = "Синхронизация..."
            if stage is not None:
                if total is not None:
                    msg = f"{msg} [{stage}/{total}]"
                else:
                    msg = f"{msg} [{stage}]"
            with st.spinner(msg):
                return func()

        return wrapper

    return decorator
