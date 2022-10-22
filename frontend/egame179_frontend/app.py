import logging
import time

import httpx
import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_server_state import server_state

from egame179_frontend.state import clean_session_state, init_server_state, init_session_state, logout
from egame179_frontend.views.login import login_form
from egame179_frontend.views.sync import fetch_data


def app() -> None:
    """Entry point for the game frontend."""
    if st.session_state.views:
        selected_option = sidebar()
        header()
        if st.session_state.synced:  # check sync between session and server state
            pass
        else:
            fetch_data()
            st.session_state.synced = True

        view_func = st.session_state.option2view[selected_option]
        view_func(st.session_state.game_state)
    else:
        login_form()


def sidebar() -> str:
    """UI sidebar."""
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
            clean_session_state()
    return selected_option


def header() -> None:
    """UI header."""
    st.markdown("### Система корпоративного управления CP v2022/10.77")
    st.title(f"Пользователь {st.session_state.user.name}")


if __name__ == "__main__":
    st.set_page_config(page_title="CP v2022/10.77", layout="wide")
    init_server_state()
    init_session_state()
    try:
        app()
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == httpx.codes.UNAUTHORIZED:
            logging.exception(f"Unauthorized access: {exc}")
            st.error("Сессия истекла, необходима повторная авторизация")
            time.sleep(1)
            logout()
        elif exc.response.is_server_error:
            logging.exception(f"Server error: {exc}")
            st.error("Ошибка сервера, повторная попытка...")
            time.sleep(1)
            clean_session_state()
        raise exc
