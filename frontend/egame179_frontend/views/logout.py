import streamlit as st

from egame179_frontend.api.models import Roles
from egame179_frontend.state.session import clean_cached_state
from egame179_frontend.views.registry import AppView, appview


@appview
class Logout(AppView):
    """Logout option."""

    idx = 99
    menu_option = "Выход"
    icon = "box-arrow-right"
    roles = Roles.root, Roles.editor, Roles.news, Roles.player

    def __init__(self) -> None:
        """Empty constructor."""

    def render(self) -> None:
        """Logout user."""  # noqa: DAR101
        st.session_state.auth_header = None
        st.session_state.views = None
        clean_cached_state()
        st.experimental_rerun()
