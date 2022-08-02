import streamlit as st
from millify import millify


def overview() -> None:
    st.title("NoName Corporation")
    state = st.session_state.player_state
    hcol1, hcol2, hcol3 = st.columns(3)
    with hcol1:
        st.metric(label="Цикл", value=state.cycle)
    with hcol2:
        st.metric(label="Баланс", value=millify(70000), delta=millify(-6500))
    with hcol3:
        st.markdown("Page 1 🎉")

    st.markdown("### Main page 🎈")
    st.markdown("Hello, %s!" % st.session_state.user)

    with st.sidebar:
        st.markdown("Additional sidebar content")
