import logging
import time
from datetime import datetime

import httpx
import streamlit as st
from streamlit_option_menu import option_menu

from egame179_frontend.state.state import clean_cached_state, init_game_state, init_session_state
from egame179_frontend.style import load_css
from egame179_frontend.views.login import login_form
from egame179_frontend.views.registry import AppView


def app() -> None:
    """Entry point for the game frontend."""
    init_session_state()
    user_views: dict[str, AppView] | None = st.session_state.views
    if user_views is None:
        login_form()
    else:
        init_game_state()
        header()
        with st.sidebar:
            menu_option = option_menu(
                "Меню",
                options=list(user_views.keys()),
                icons=[view.icon for view in user_views.values()],
                menu_icon="cast",
                default_index=0,
                key="option_menu",
            )
            under_menu_block()
        # render current app view
        user_views[menu_option].render()


def header() -> None:
    """UI header."""
    st.markdown("## Система корпоративного управления CP v2023/04.77")
    st.markdown("---")


def under_menu_block() -> None:
    """UI block under menu."""
    st.button("Обновить данные", on_click=clean_cached_state)
    st.markdown("---")
    st.markdown(f"*User: {st.session_state.user.name}*")
    st.markdown(f"*Last update: {datetime.now().isoformat()}*")
    st.markdown(f"*Cycle interim: {st.session_state.interim_block}*")


def http_exception_handler(exc: httpx.HTTPStatusError) -> None:
    """Handle HTTPStatus exceptions.

    Args:
        exc (httpx.HTTPStatusError): exception.

    Raises:
        exc: not a auth / server exception.
    """
    logging.exception(exc)
    if exc.response.status_code == httpx.codes.UNAUTHORIZED:
        # logout
        st.session_state.auth_header = None
        st.session_state.views = None
        error_spinner("Сессия истекла, необходима повторная авторизация", sleep=2)
    elif exc.response.is_server_error:
        error_spinner("Ошибка сервера", sleep=5, exc=exc)
    else:
        raise exc  # raise any other exception


def error_spinner(error: str, sleep: int, exc: Exception | None = None) -> None:
    """Rerun app with error and spinner.

    Args:
        error (str): error message.
        sleep (int): sleep time in seconds.
        exc (Exception, optional): handled exception. Defaults to None.
    """
    st.error(error)
    if exc is not None:
        st.exception(exc)
    with st.spinner(f"Повторная попытка через {sleep}с..."):
        time.sleep(sleep)
    clean_cached_state()
    st.experimental_rerun()


if __name__ == "__main__":
    st.set_page_config(page_title="CP v2023/04.77", layout="wide")
    load_css()
    try:
        app()
    except httpx.HTTPStatusError as exc:
        http_exception_handler(exc)
    except httpx.ConnectError as exc:
        error_spinner("Сервер недоступен", sleep=5, exc=exc)
    except ConnectionRefusedError as exc:
        error_spinner("Сервер недоступен", sleep=5, exc=exc)
