import streamlit as st

from egame179_frontend.api.auth import get_auth_header, get_user


def login_callback() -> None:
    """Login callback, using backend for auth."""
    auth_header = get_auth_header(login=st.session_state.login, password=st.session_state.password)
    if auth_header is not None:
        user = get_user(auth_header)
        if user is not None:
            st.session_state.auth_header = auth_header
            st.session_state.user = user


def login_form() -> None:
    """Streamlit login form."""
    st.markdown(
        "<center><h2>Необходим авторизованный доступ</h2></center>",
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)
    _, col, _ = st.columns([1.5, 1, 1.5])
    with col:
        with st.form(key="login_form"):
            st.text("Corporate Portal [CP] v2022/10.77")
            st.text_input("Логин:", key="login")
            st.text_input("Пароль:", type="password", key="password")
            if st.form_submit_button("Войти", on_click=login_callback):
                if st.session_state.user is None:
                    st.error("Неверный логин или пароль", icon="🚨")
    st.markdown(
        "<center>В случае проблем с авторизацией, обратитесь к вашему корпоративному администратору.</center>",
        unsafe_allow_html=True,
    )
