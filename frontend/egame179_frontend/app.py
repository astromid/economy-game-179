import streamlit as st
from streamlit_option_menu import option_menu

from egame179_frontend.api import mock
from egame179_frontend.views.login import login_form, refresh
from egame179_frontend.views.root import ROOT_VIEWS
from egame179_frontend.views.user import USER_VIEWS


def init_state() -> None:
    """Initialize the state of the streamlit app."""
    if "user" not in st.session_state:
        st.session_state.user = None

    match st.session_state.user:
        case None:
            st.session_state.views = ()
        case "root":
            st.session_state.views = ROOT_VIEWS
            st.session_state.game_state = {"mode": "GOD"}
        case _:
            st.session_state.views = USER_VIEWS
            st.session_state.game_state = mock.mock_player_state()
    st.session_state.option2view = {view.menu_option: view.page_func for view in st.session_state.views}


def app() -> None:
    """Entry point for the game frontend."""
    if st.session_state.views:
        with st.sidebar:
            selected_option = option_menu(
                "Меню",
                options=[view.menu_option for view in st.session_state.views],
                icons=[view.icon for view in st.session_state.views],
                menu_icon="cast",
                default_index=0,
                key="option_menu",
            )
            if st.button("Обновить данные"):
                refresh()
        view_func = st.session_state.option2view[selected_option]
        game_state = st.session_state.game_state

        st.markdown("### Система корпоративного управления CP v2022/10.77")
        st.title(f"{game_state.player.name} Corporation")
        view_func(game_state)
    else:
        login_form()


if __name__ == "__main__":
    st.set_page_config(page_title="CP v2022/10.77", layout="wide")
    init_state()
    app()
