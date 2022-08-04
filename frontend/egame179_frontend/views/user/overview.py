import streamlit as st
from millify import millify

from egame179_frontend.api.models import PlayerState


def overview() -> None:
    state: PlayerState = st.session_state.game_state
    hcol1, hcol2, hcol3 = st.columns(3)
    with hcol1:
        st.metric(label="Цикл", value=state.cycle)
    with hcol2:
        st.metric(label="Баланс", value=millify(state.balance), delta=millify(state.balance_delta))
    with hcol3:
        st.markdown("Page 1 🎉")

    st.markdown("### Main page 🎈")

    with st.sidebar:
        st.markdown("Additional sidebar content")
