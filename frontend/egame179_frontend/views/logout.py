import streamlit as st

from egame179_frontend.api.user import UserRoles
from egame179_frontend.state import clean_cached_state
from egame179_frontend.views.registry import AppView, appview


@appview
class Logout(AppView):
    """Logout option."""

    idx = 99
    name = "Выход"
    icon = "box-arrow-right"
    roles = (
        UserRoles.ROOT.value,
        UserRoles.NEWS.value,
        UserRoles.PLAYER.value,
    )

    def __init__(self) -> None:
        """Empty constructor."""

    def render(self) -> None:
        """Logout user."""
        st.session_state.auth_header = None
        st.session_state.views = None
        st.session_state.game = None
        clean_cached_state()
        st.experimental_rerun()
