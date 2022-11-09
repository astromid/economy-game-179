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

    synced: bool = False
    cycle: api_models.Cycle | None = None


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
    """Initialize game state after user auth."""
    user: api_models.User = st.session_state.user
    if st.session_state.game is None:
        # first run for this user, we need to create empty game states
        match user.role:
            case api_models.Roles.root:
                init_server_state()  # init empty server state
                st.session_state.game = RootState()
            case api_models.Roles.player:
                st.session_state.game = PlayerState()
    


def init_server_state() -> None:
    """Initialize server state (from root)."""
    with server_state_lock["game"]:
        if "game" not in server_state:
            server_state["game"] = SharedGameState()


def check_server_state_sync() -> None:
    """Check if server state is actual.

    Raises:
        WaitingForMasterError: if server state is not actual.
    """
    if not server_state.game.synced:
        raise WaitingForMasterError


def check_sync_with_shared() -> bool:
    """Check if session game state is synced with server.

    Returns:
        bool: True if user state is synced with shared, False otherwise.
    """
    player_state: PlayerState = st.session_state.game
    shared_state: SharedGameState = server_state.game
    return player_state.cycle == shared_state.cycle
