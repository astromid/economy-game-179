import streamlit as st

from egame179_frontend.api.mock import mock_auth
from egame179_frontend.views import View


def login_callback() -> None:
    """Login callback, using backend for auth."""
    st.session_state.user = mock_auth(login=st.session_state.login, password=st.session_state.password)


def login_form() -> None:
    """Streamlit login form."""
    st.markdown(
        "<center> <h2>Необходим авторизованный доступ</h2> </center>",
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)
    _, col, _ = st.columns([1.5, 1, 1.5])
    with col:
        with st.form(key="login_form"):
            st.text("Corporate Portal [CP] v20.22")
            st.text_input("Логин:", key="login")
            st.text_input("Пароль:", type="password", key="password")
            if st.form_submit_button("Войти", on_click=login_callback):
                if st.session_state.user is None:
                    st.error("Неверный логин или пароль")
    st.markdown(
        "<center>В случае проблем с авторизацией, обратитесь к корпоративному администратору</center>",
        unsafe_allow_html=True,
    )


def logout() -> None:
    """Clear user session."""
    st.session_state.user = None
    st.experimental_memo.clear()
    st.experimental_rerun()


LOGOUT_OPTION = View(menu_option="Выход", icon="box-arrow-right", page_func=logout)
