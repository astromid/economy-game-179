from dataclasses import dataclass

import streamlit as st

from egame179_frontend.models import Cycle, Roles
from egame179_frontend.views.registry import AppView, appview


@dataclass
class _ViewState:
    cycle: int
    started: str
    finished: str | None


@appview
class RootDashboard(AppView):
    """Root game dashboard."""

    idx = 0
    menu_option = "Статус"
    icon = "house"
    roles = [Roles.root]

    def __init__(self) -> None:
        self.state: _ViewState | None = None

    @st.experimental_memo  # type: ignore
    def cache_state(self) -> None:
        """Cache state of the view."""
        pass

    def render(self) -> None:
        """Render view."""
        _cycle_stats(self.state)
        st.markdown("---")
        _cycle_controls(self.state)


def _cycle_stats(state: _ViewState) -> None:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Текущий цикл", state.cycle)
    with col2:
        st.metric("Начался", state.started)
    with col3:
        st.metric("Закончился", state.finished)


def _cycle_controls(state: _ViewState) -> None:
    col1, col2 = st.columns(2)
    with col1:
        st.button("Завершить цикл", disabled=state.finished is not None)
    with col2:
        st.button("Начать новый цикл", disabled=state.finished is None)
