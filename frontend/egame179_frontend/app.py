import streamlit as st
from streamlit_option_menu import option_menu

from egame179_frontend.views.dashboard import dashboard
from egame179_frontend.views.main_page import main_page

VIEWS = {
    "Main page": {"view": main_page, "icon": "gear"},
    "Dashboard": {"view": dashboard, "icon": "house"},
}


def login_callback():
    st.session_state.user = "root"


def logout_callback():
    st.session_state.user = None


def login_form():
    with st.form(key="login_form"):
        st.text("Корпоративная система v2.0.77")
        st.text_input("Логин:", key="login")
        st.text_input("Пароль:", type="password", key="password")
        if st.form_submit_button("Войти", on_click=login_callback):
            if not st.session_state.user:
                st.error("Неверный логин или пароль")


def app():
    if st.session_state.user is not None:
        VIEWS["Exit"] = {"view": logout_callback, "icon": "box-arrow-right"}

    with st.sidebar:
        view = option_menu(
            "Main Menu",
            options=list(VIEWS.keys()),
            icons=[view["icon"] for view in VIEWS.values()],
            menu_icon="cast",
            default_index=0,
        )

    if st.session_state.user is None:
        st.markdown("## Пожалуйста, авторизуйтесь для доступа к операционной информации.")
        with st.sidebar:
            login_form()

    VIEWS[view]["view"]()
    if view == "Exit":
        st.experimental_rerun()


if __name__ == "__main__":
    if "user" not in st.session_state:
        st.session_state["user"] = None
    title = f"CP 2.0.20: {st.session_state.user}" if st.session_state.user else "CP 2.0.20: Авторизация"
    st.set_page_config(page_title=title, layout="wide")
    app()
