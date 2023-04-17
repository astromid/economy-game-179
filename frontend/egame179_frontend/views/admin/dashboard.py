from dataclasses import dataclass
from datetime import datetime

import streamlit as st

from egame179_frontend.api import CycleAPI
from egame179_frontend.api.user import UserRoles
from egame179_frontend.state.state import RootState
from egame179_frontend.views.registry import AppView, appview


@dataclass
class _ViewData:
    cycle: int
    ts_start: str | None
    ts_finish: str | None


@st.cache_data(max_entries=1)
def _cache_view_data(
    cycle: int,
    ts_start: datetime | None,
    ts_finish: datetime | None,
) -> _ViewData:
    return _ViewData(
        cycle,
        ts_start.isoformat() if ts_start is not None else None,
        ts_finish.isoformat() if ts_finish is not None else None,
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

        col1, col2 = st.columns([2, 1])
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
        st.metric("Начался", state.ts_start)
    with col3:
        st.metric("Закончился", state.ts_finish)


def _cycle_controls(state: _ViewData) -> None:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.button("Новый цикл", on_click=CycleAPI.create_cycle, disabled=state.ts_finish is None)
    with col2:
        st.button("Начать цикл", on_click=CycleAPI.start_cycle, disabled=state.ts_start is not None)
    with col3:
        st.button(
            "Завершить цикл",
            on_click=CycleAPI.finish_cycle,
            disabled=(state.ts_start is None) or (state.ts_finish is not None),
        )
