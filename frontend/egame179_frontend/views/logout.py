import streamlit as st

from egame179_frontend.models import Roles
from egame179_frontend.state import clean_session_state
from egame179_frontend.views.registry import AppView, appview


@appview
class Logout(AppView):
    """Logout option."""

    idx = 99
    menu_option = "Выход"
    icon = "box-arrow-right"
    roles = [Roles.root, Roles.editor, Roles.news, Roles.player]

    def __init__(self) -> None:
        """Empty constructor."""

    def render(self) -> None:
        """Logout user."""  # noqa: DAR101
        st.session_state.auth_header = None
        st.session_state.user = None
        clean_session_state()
