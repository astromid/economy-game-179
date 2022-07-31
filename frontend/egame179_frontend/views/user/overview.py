import streamlit as st


def overview() -> None:
    st.markdown("## Система корпоративного управления CP/20.22")
    st.title("NoName Corporation")
    state = st.session_state.player_state
    hcol1, hcol2, hcol3 = st.columns(3)
    with hcol1:
        st.metric(label="Цикл", value=state.cycle)
    with hcol2:
        st.metric(label="Баланс", value=None)
    with hcol3:
        st.markdown("Page 1 🎉")

    st.markdown("### Main page 🎈")
    st.markdown("Hello, %s!" % st.session_state.user)

    with st.sidebar:
        st.markdown("Additional sidebar content")
