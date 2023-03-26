from typing import ClassVar

import streamlit as st

from egame179_frontend.api.user import UserRoles
from egame179_frontend.state.state import clean_cached_state
from egame179_frontend.views.registry import appview


@appview
class Logout:
    """Logout option."""

    idx: ClassVar[int] = 99
    name: ClassVar[str] = "Выход"
    icon: ClassVar[str] = "box-arrow-right"
    roles: ClassVar[tuple[str, ...]] = (
        UserRoles.ROOT.value,
        UserRoles.EDITOR.value,
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
