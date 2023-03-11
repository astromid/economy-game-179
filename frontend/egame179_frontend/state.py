from dataclasses import dataclass

import streamlit as st
from streamlit_server_state import server_state, server_state_lock

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
    with server_state_lock["block_input"]:
        if "block_input" not in server_state:
            server_state.block_input = True


def clean_cached_state() -> None:
    """Refresh user session."""
    st.session_state.game = None
    st.cache_data.clear()


def init_game_state() -> None:
    """Initialize game state after user auth."""
    user: api_models.User = st.session_state.user
    if st.session_state.game is None:  # first run for this user, we need to create empty game states
        match user.role:
            case api_models.Roles.root:
                st.session_state.game = RootState()
            case api_models.Roles.player:
                st.session_state.game = PlayerState()
