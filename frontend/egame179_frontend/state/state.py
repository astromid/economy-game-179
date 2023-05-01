from dataclasses import fields

import streamlit as st

from egame179_frontend.api.cycle import CycleAPI
from egame179_frontend.api.user import User, UserRoles
from egame179_frontend.state.player import PlayerState
from egame179_frontend.state.root import RootState


def init_session_state() -> None:
    """Initialize the session state of the streamlit app."""
    init_state = {
        "auth_header": None,
        "user": None,
        "views": None,
        "game": None,
        "interim_block": False,
    }
    for field, init_value in init_state.items():
        if field not in st.session_state:
            st.session_state[field] = init_value


def clean_cached_state() -> None:
    """Refresh user session."""
    st.session_state.game = None
    st.cache_data.clear()


def init_game_state() -> None:
    """Initialize game state after user auth."""
    server_cycle = CycleAPI.get_cycle()  # get cycle info from server and check sync
    st.session_state.interim_block = (server_cycle.ts_start is None) or (server_cycle.ts_finish is not None)

    user: User = st.session_state.user
    if st.session_state.game is None:  # first run for this user, we need to create empty game states
        match user.role:
            case UserRoles.ROOT.value:
                st.session_state.game = RootState(cycle=server_cycle)
            case UserRoles.PLAYER.value:
                st.session_state.game = PlayerState(cycle=server_cycle)
            case _:
                # TODO: support news & editor roles
                raise ValueError(f"Unsupported user.role {user.role}")
    elif st.session_state.game.cycle != server_cycle:
        st.session_state.game.cycle = server_cycle
        # clear cached state (except new cycle & constant markets graph)
        for field in fields(st.session_state.game):
            if field.name not in {"cycle", "_markets"}:
                setattr(st.session_state.game, field.name, None)
