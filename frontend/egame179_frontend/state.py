from dataclasses import dataclass
from types import MappingProxyType

import streamlit as st
from streamlit_server_state import server_state, server_state_lock

from egame179_frontend.api import models as api_models

SESSION_INIT_STATE = MappingProxyType(
    {
        "auth_header": None,
        "user": None,
        "views": None,
        "game": None,
    },
)


@dataclass
class SharedGameState:
    """Shared game state for all players."""

    cycle: api_models.Cycle


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
    for field, init_value in SESSION_INIT_STATE.items():
        if field not in st.session_state:
            st.session_state[field] = init_value


def clean_cached_state() -> None:
    """Refresh user session."""
    st.session_state.game = None
    st.experimental_memo.clear()  # type: ignore


class WaitingForMasterError(Exception):
    """Game is waiting for master actions."""


def init_game_state() -> None:
    """Initialize game state for auth user.

    Raises:
        WaitingForMasterError: if game is waiting for master actions.
    """
    user: api_models.User = st.session_state.user
    if user.role == api_models.Roles.root:
        # root game initialization (server state, shared game info)
        init_server_state()
        if not check_shared_state():
            with server_state_lock["game"]:
                server_state.game = fetch_shared_state()
    else:
        if server_state.game is None:
            raise WaitingForMasterError
        
        if not check_sync_status():
            clean_cached_state()


def init_server_state() -> None:
    """Initialize server state (from root)."""
    with server_state_lock["game"]:
        if "game" not in server_state:
            server_state.game = None


def check_sync_with_shared() -> bool:
    """Check if session game state is synced with server.

    Returns:
        bool: True if user state is synced with shared, False otherwise.
    """
    player_state: PlayerState = st.session_state.game
    shared_state: SharedGameState = server_state.game
    return player_state.cycle == shared_state.cycle
