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


@st.cache_data(max_entries=1)
def _cache_view_data(
    cycle: int,
    ts_start: datetime | None,
) -> _ViewData:
    return _ViewData(
        cycle,
        ts_start.time().isoformat() if ts_start is not None else None,
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
        state: RootState = st.session_state.game
        self.state = _cache_view_data(cycle=state.cycle.id, ts_start=state.cycle.ts_start)  # type: ignore

        col1, col2 = st.columns([2, 1], gap="medium")
        with col1:
            _cycle_stats(self.state)
            st.markdown("---")
            _cycle_controls(self.state)
        with col2:
            st.write("WIP")


def _cycle_stats(state: _ViewData) -> None:
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Текущий цикл", state.cycle)
    with col2:
        st.metric("Начался", state.ts_start)


def _cycle_controls(state: _ViewData) -> None:
    col1, col2 = st.columns(2)
    with col1:
        st.button("Начать цикл", on_click=CycleAPI.start_cycle, disabled=state.ts_start is not None)
    with col2:
        st.button("Завершить цикл", on_click=CycleAPI.finish_cycle, disabled=state.ts_start is None)
    if st.button("! Реинициализация игры !"):

        import subprocess
        result = subprocess.run(["./_reinit_db.sh"], stdout=subprocess.PIPE, text=True)
        st.write("stdout:", result.stdout)
