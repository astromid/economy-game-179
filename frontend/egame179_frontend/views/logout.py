from typing import ClassVar

import streamlit as st

from egame179_frontend.api.models import Roles
from egame179_frontend.state import clean_cached_state
from egame179_frontend.views.registry import appview


@appview
class Logout:
    """Logout option."""

    idx: ClassVar[int] = 99
    menu_option: ClassVar[str] = "Выход"
    icon: ClassVar[str] = "box-arrow-right"
    roles: ClassVar[tuple[str, ...]] = Roles.root, Roles.editor, Roles.news, Roles.player

    def __init__(self) -> None:
        """Empty constructor."""

    def render(self) -> None:
        """Logout user."""
        st.session_state.auth_header = None
        st.session_state.views = None
        clean_cached_state()
        st.experimental_rerun()
