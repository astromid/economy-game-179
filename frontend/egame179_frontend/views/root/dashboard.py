import streamlit as st

from egame179_frontend.api.models import Cycle


def dashboard(game_state: Cycle) -> None:
    """Root dashboard view."""
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Текущий цикл", game_state.cycle)
    with col2:
        st.metric("Начался", game_state.started)
    with col3:
        st.metric("Закончился", game_state.finished)
