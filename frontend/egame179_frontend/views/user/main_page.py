import streamlit as st


def main_page():
    st.title("NoName Corporation")
    st.markdown("# Система корпоративного управления CP/20.22")
    hcol1, hcol2, hcol3 = st.columns(3)
    with hcol1:
        st.metric(label="Цикл", value=None)
    with hcol2:
        st.metric(label="Баланс", value=None)

    st.markdown("# Main page 🎈")
    st.markdown("# Page 1 🎉")
    st.markdown("Hello, %s!" % st.session_state.user)
    with st.sidebar:
        st.markdown("SIDEBAR!")
