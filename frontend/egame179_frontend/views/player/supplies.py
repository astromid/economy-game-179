import streamlit as st

from egame179_frontend.api.user import UserRoles
from egame179_frontend.state.state import PlayerState
from egame179_frontend.views.registry import AppView, appview


def sales_view(state: PlayerState) -> None:
    st.markdown("## Поставки")
    # В форме поставки должны отображаться только те товары, которые есть в наличии
    with st.expander("Активные поставки"):
        col1, col2, col3 = st.columns([1, 1, 3])
        with col1:
            st.text("Рынок 1")
            st.text("Рынок 2")
        with col2:
            st.text("50%")
            st.text("33%")
        with col3:
            st.progress(0.5)
            st.progress(0.33)


@appview
class SuppliesView(AppView):
    """Supplies AppView."""

    idx = 13
    name = "Склады и поставки"
    icon = "box-seam"
    roles = (UserRoles.PLAYER.value,)

    def __init__(self) -> None:
        self.view_data: _ViewData | None = None

    def render(self) -> None:
        """Render view."""
        state: PlayerState = st.session_state.game
