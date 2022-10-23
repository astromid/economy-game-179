import logging
import time

import httpx
import streamlit as st
from streamlit_option_menu import option_menu

from egame179_frontend.state import clean_session_state, init_session_state
from egame179_frontend.views.login import login_form
from egame179_frontend.views.registry import AppView


def app() -> None:
    """Entry point for the game frontend."""
    if st.session_state.views is None:
        login_form()
    else:
        header()
        selected_option = sidebar()

        current_view: AppView = st.session_state.views[selected_option]
        current_view.render()


def header() -> None:
    """UI header."""
    st.markdown("### Система корпоративного управления CP v2022/10.77")
    st.title(f"Пользователь {st.session_state.user.name}")


def sidebar() -> str:
    """UI sidebar.

    Returns:
        str: selected option.
    """
    with st.sidebar:
        selected_option = option_menu(
            "Меню",
            options=list(st.session_state.views.keys()),
            icons=[view.icon for view in st.session_state.views.values()],
            menu_icon="cast",
            default_index=0,
            key="option_menu",
        )
        if st.button("Обновить данные"):
            clean_session_state()
    return selected_option


def http_exception_handler(exc: httpx.HTTPStatusError) -> None:
    """Handle HTTPStatus exceptions.

    Args:
        exc (httpx.HTTPStatusError): exception.

    Raises:
        exc: not a auth / server exception.
    """
    logging.exception(exc)
    if exc.response.status_code == httpx.codes.UNAUTHORIZED:
        st.error("Сессия истекла, необходима повторная авторизация")
        time.sleep(1)
        # logout
        st.session_state.auth_header = None
        st.session_state.user = None
        clean_session_state()
    elif exc.response.is_server_error:
        st.error("Ошибка сервера, повторная попытка через 3с...")
        st.exception(exc)
        time.sleep(3)
        clean_session_state()
    raise exc  # raise any other exception


if __name__ == "__main__":
    st.set_page_config(page_title="CP v2022/10.77", layout="wide")
    init_session_state()
    try:
        app()
    except httpx.HTTPStatusError as exc:
        http_exception_handler(exc)
