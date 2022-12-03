from dataclasses import dataclass

import streamlit as st

from egame179_frontend.api import models as api_models


@dataclass
class RootState:
    """Root game state."""

    cycle: api_models.Cycle | None = None


@dataclass
class PlayerState:
    """Player game state."""

    cycle: api_models.Cycle | None = None


def init_session_state() -> None:
    """Initialize the session state of the streamlit app."""
    init_state = {
        "auth_header": None,
        "user": None,
        "views": None,
        "game": None,
    }
    for field, init_value in init_state.items():
        if field not in st.session_state:
            st.session_state[field] = init_value


def clean_cached_state() -> None:
    """Refresh user session."""
    st.session_state.game = None
    st.experimental_memo.clear()  # type: ignore
