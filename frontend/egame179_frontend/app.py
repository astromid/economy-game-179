import extra_streamlit_components as stx
import streamlit as st
from streamlit_option_menu import option_menu

from egame179_frontend.api.mock import _mock_player_state
from egame179_frontend.views.login import login_form
from egame179_frontend.views.root import ROOT_VIEWS
from egame179_frontend.views.user import USER_VIEWS


def init_state() -> None:
    """Initialize the state of the streamlit app."""
    if "user" not in st.session_state:
        st.session_state.user = None

    match st.session_state.user:
        case None:
            st.session_state.views = []
        case "root":
            st.session_state.views = ROOT_VIEWS
        case _:
            st.session_state.views = USER_VIEWS
    st.session_state.option2view = {view.menu_option: view.page_func for view in st.session_state.views}
    st.session_state.player_state = _mock_player_state()


def app() -> None:
    """Entry point for the game frontend."""
    if st.session_state.user is None:
        login_form()

    if st.session_state.views:
        with st.sidebar:
            selected_option = option_menu(
                "Меню",
                options=[view.menu_option for view in st.session_state.views],
                icons=[view.icon for view in st.session_state.views],
                menu_icon="cast",
                default_index=0,
            )

        view_func = st.session_state.option2view[selected_option]
        view_func()


if __name__ == "__main__":
    st.set_page_config(page_title="CP / 20.22", layout="wide")
    init_state()
    app()