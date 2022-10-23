from types import MappingProxyType

import streamlit as st

SESSION_INIT_STATE = MappingProxyType({
    "auth_header": None,
    "user": None,
    "views": None,
    "game": None,
    "synced": False,
})


def init_session_state() -> None:
    """Initialize the session state of the streamlit app."""
    for field, init_value in SESSION_INIT_STATE.items():
        if field not in st.session_state:
            st.session_state[field] = init_value


def clean_session_state() -> None:
    """Refresh user session."""
    st.session_state.synced = False
    st.experimental_memo.clear()  # type: ignore
    st.experimental_rerun()
