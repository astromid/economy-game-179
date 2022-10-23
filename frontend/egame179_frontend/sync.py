import streamlit as st
from streamlit_server_state import server_state, server_state_lock

from egame179_frontend.api.fetch import get_fetch_func


def fetch_data() -> None:
    """Fetch data from backend."""
    fetch_func = get_fetch_func(st.session_state.user.role)
    with st.spinner("Загрузка данных..."):
        st.session_state.game_state = fetch_func()
