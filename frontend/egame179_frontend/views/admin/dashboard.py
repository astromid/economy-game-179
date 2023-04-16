from dataclasses import dataclass
from datetime import datetime

import streamlit as st

from egame179_frontend.api.user import UserRoles
from egame179_frontend.state.state import RootState
from egame179_frontend.views.registry import AppView, appview


@dataclass
class _ViewData:
    cycle: int
    started: str | None
    finished: str | None


@st.cache_data(max_entries=1)
def _cache_view_data(
    cycle: int,
    started: datetime | None,
    finished: datetime | None,
) -> _ViewData:
    return _ViewData(
        cycle,
        started.isoformat() if started is not None else None,
        finished.isoformat() if finished is not None else None,
    )


@appview
class RootDashboard(AppView):
    """Root game dashboard AppView."""

    idx = 0
    name = "Обзор"
    icon = "house"
    roles = (UserRoles.ROOT.value,)

    def __init__(self) -> None:
        self.state: _ViewData | None = None

    def render(self) -> None:
        """Render view."""
        game_state: RootState = st.session_state.game
        self.state = _cache_view_data(**game_state.cycle.dict())  # type: ignore

        col1, col2 = st.columns(2)
        with col1:
            _cycle_stats(self.state)
            st.markdown("---")
            _cycle_controls(self.state)
        with col2:
            st.write("WIP")


def _cycle_stats(state: _ViewData) -> None:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Текущий цикл", state.cycle)
    with col2:
        st.metric("Начался", state.started)
    with col3:
        st.metric("Закончился", state.finished)


def _cycle_controls(state: _ViewData) -> None:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.button("Новый цикл", disabled=state.finished is not None)
    with col2:
        st.button("Начать цикл", disabled=state.started is not None)
    with col3:
        st.button("Завершить цикл", disabled=state.finished is not None)
