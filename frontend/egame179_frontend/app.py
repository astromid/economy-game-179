import logging
import time

import httpx
import streamlit as st
from streamlit_option_menu import option_menu

from egame179_frontend.state import clean_session_state, init_server_state, init_session_state, logout
from egame179_frontend.views.login import login_form


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
                clean_session_state()
        view_func = st.session_state.option2view[selected_option]

        st.markdown("### Система корпоративного управления CP v2022/10.77")
        st.title(f"Пользователь {st.session_state.user.name}")
        view_func(st.session_state.game_state)
    else:
        login_form()


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
        raise exc
