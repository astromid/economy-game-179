import streamlit as st


def dashboard(*args) -> None:
    st.markdown("# Root dashboard ❄️")
    st.button("Закончить цикл")
    st.write(st.session_state.game_state)
