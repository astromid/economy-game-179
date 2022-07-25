import streamlit as st
from streamlit_option_menu import option_menu

from egame179_frontend.login import login_form, logout
from egame179_frontend.views.dashboard import dashboard
from egame179_frontend.views.main_page import main_page


def init_state():
    if "user" not in st.session_state:
        st.session_state["user"] = None

    st.session_state.views = {
        "Main page": {"view": main_page, "icon": "gear"},
        "Dashboard": {"view": dashboard, "icon": "house"},
    }


def app():
    if st.session_state.user is not None:
        st.session_state.views["Exit"] = {"view": logout, "icon": "box-arrow-right"}

    with st.sidebar:
        view = option_menu(
            "Main Menu",
            options=list(st.session_state.views.keys()),
            icons=[view["icon"] for view in st.session_state.views.values()],
            menu_icon="cast",
            default_index=0,
        )

    if st.session_state.user is None:
        st.markdown("## Пожалуйста, авторизуйтесь для доступа к операционной информации.")
        with st.sidebar:
            login_form()

    st.session_state.views[view]["view"]()


if __name__ == "__main__":
    init_state()
    title = f"CP 2.0.20: {st.session_state.user}" if st.session_state.user else "CP 2.0.20: Авторизация"
    st.set_page_config(page_title=title, layout="wide")
    app()
