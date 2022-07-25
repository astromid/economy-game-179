import streamlit as st


def login_callback():
    st.session_state.user = "root"


def login_form():
    with st.form(key="login_form"):
        st.text("Корпоративная система v2.0.77")
        st.text_input("Логин:", key="login")
        st.text_input("Пароль:", type="password", key="password")
        if st.form_submit_button("Войти", on_click=login_callback):
            if not st.session_state.user:
                st.error("Неверный логин или пароль")


def logout():
    st.session_state.user = None
    st.experimental_rerun()
