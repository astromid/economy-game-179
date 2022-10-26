from types import MappingProxyType

import streamlit as st
from streamlit_server_state import server_state, server_state_lock

from egame179_frontend.models import Roles, User

SESSION_INIT_STATE = MappingProxyType(
    {
        "auth_header": None,
        "user": None,
        "views": None,
        "game": None,
        "synced": False,
    },
)


def init_game_state() -> None:
    """Initialize game state (session, server)."""
    init_session_state()  # firstly init session state
    user: User | None = st.session_state.user
    if user is not None:
        if user.role == Roles.root:
            init_server_state()
        else:
            check_game_started()


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
