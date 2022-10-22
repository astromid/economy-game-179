from types import MappingProxyType

import streamlit as st

from egame179_frontend.api import mock
from egame179_frontend.api.models import User
from egame179_frontend.views import View
from egame179_frontend.views.root import ROOT_VIEWS
from egame179_frontend.views.user import USER_VIEWS

SESSION_INIT_STATE = MappingProxyType({
    "auth_header": None,
    "user": None,
    "views": (),
    "synced": False,
})


def init_server_state() -> None:
    """Initialize the server state of the streamlit app."""
    pass  # noqa: WPS420


def init_session_state() -> None:
    """Initialize the session state of the streamlit app."""
    for field, init_value in SESSION_INIT_STATE.items():
        if field not in st.session_state:
            st.session_state[field] = init_value

    match st.session_state.user:
        case User(role="player"):
            user_views = USER_VIEWS
            st.session_state.game_state = mock.mock_player_state()
        case User(role="root"):
            user_views = ROOT_VIEWS
            st.session_state.game_state = {"user": User}
        case User(role="editor"):
            user_views = ROOT_VIEWS
            st.session_state.game_state = {"user": User}
        case User(role="news"):
            user_views = ROOT_VIEWS
            st.session_state.game_state = {"user": User}
        case _:
            user_views = ()
    if user_views:  # add logout option
        st.session_state.views = user_views + (View(menu_option="Выход", icon="box-arrow-right", page_func=logout),)
    else:
        st.session_state.views = user_views
    st.session_state.option2view = {view.menu_option: view.page_func for view in st.session_state.views}


def logout(*args) -> None:
    """Logout user."""  # noqa: DAR101
    st.session_state.auth_header = None
    st.session_state.user = None
    clean_session_state()


def clean_session_state() -> None:
    """Refresh user session."""
    st.session_state.synced = False
    st.experimental_memo.clear()  # type: ignore
    st.experimental_rerun()
