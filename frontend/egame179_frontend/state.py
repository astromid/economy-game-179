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
        "synced": False,
    },
)


def init_session_state() -> None:
    """Initialize the session state of the streamlit app."""
    for field, init_value in SESSION_INIT_STATE.items():
        if field not in st.session_state:
            st.session_state[field] = init_value


def init_server_state() -> None:
    """Initialize shared server state (from root)."""
    with server_state_lock["game"]:
        if "game" not in server_state:
            server_state.game = None


def clean_cached_state() -> None:
    """Refresh user session."""
    st.session_state.synced = False
    st.experimental_memo.clear()  # type: ignore


class GameNotStartedError(Exception):
    """Game not started error."""


def check_game_started() -> None:
    """Check if game started (for user).

    Raises:
        GameNotStartedError: game not started.
    """
    game_state = server_state.get("game", None)
    if game_state is None:
        raise GameNotStartedError


@dataclass
class SharedGameState:
    """Shared game state for all players."""

    cycle: api_models.Cycle


@dataclass
class RootState:
    """Root game state."""

    cycle: api_models.Cycle | None


@dataclass
class PlayerState:
    """Player game state."""

    cycle: api_models.Cycle | None


def init_game_state() -> None:
    """Initialize game state for auth user."""
    user: api_models.User = st.session_state.user
    if user.role == api_models.Roles.root:
        init_server_state()
    else:
        check_game_started()
        if st.session_state.synced:
            st.session_state.synced = check_sync_status()


def check_sync_status() -> bool:
    """Check if session game state is synced with server.

    Returns:
        bool: True if user state is synced with root, False otherwise.
    """
    player_state: PlayerState = st.session_state.game
    shared_state: SharedGameState = server_state.game
    return player_state.cycle == shared_state.cycle
