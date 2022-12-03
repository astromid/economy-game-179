import streamlit as st
from streamlit_server_state import server_state

from egame179_frontend.api import models as api_models
from egame179_frontend.state.session import PlayerState, RootState
from egame179_frontend.state.shared import SharedGameState, fetch_shared_state, init_server_state


def init_game_state() -> None:
    """Initialize game state after user auth."""
    user: api_models.User = st.session_state.user
    if st.session_state.game is None:  # first run for this user, we need to create empty game states
        match user.role:
            case api_models.Roles.root:
                init_server_state()  # init empty server state
                st.session_state.game = RootState()
            case api_models.Roles.player:
                st.session_state.game = PlayerState()


class WaitingForMasterError(Exception):
    """Game is waiting for master actions."""


def check_state_sync():
    """Check if state is synced.

    If shared state is not synced and user is root, fetch it.

    Raises:
        WaitingForMasterError: if shared state is outdated.
    """
    shared_state: SharedGameState | None = server_state.get("game")
    if shared_state is None or not shared_state.synced:  # check shared state
        user: api_models.User = st.session_state.user
        if user.role == api_models.Roles.root:
            fetch_shared_state()
        else:
            raise WaitingForMasterError
    if not check_session_sync():  # check session state
        st.session_state.game.cycle = None  # reset cycle as flag to refresh state


def check_session_sync() -> bool:
    """Check if session game state is synced with shared.

    Returns:
        bool: True if user state is synced with shared, False otherwise.
    """
    player_state: PlayerState | RootState = st.session_state.game
    shared_state: SharedGameState = server_state.game
    return player_state.cycle == shared_state.cycle
