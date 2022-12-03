from dataclasses import dataclass
from datetime import datetime
from typing import ClassVar

import streamlit as st
from streamlit_server_state import server_state

from egame179_frontend.api.cycle import CycleAPI
from egame179_frontend.api.models import Roles
from egame179_frontend.fetch_ui import fetch_spinner
from egame179_frontend.state.session import RootState
from egame179_frontend.state.shared import SharedGameState
from egame179_frontend.views.registry import appview


@dataclass
class _ViewState:
    cycle: int
    started: str
    finished: str | None


@st.experimental_memo(max_entries=1)  # type: ignore
def _cache_view_state(
    cycle: int,
    started: datetime,
    finished: datetime | None,
) -> _ViewState:
    return _ViewState(
        cycle,
        started.isoformat(),
        finished.isoformat() if finished is not None else None,
    )


@appview
class RootDashboard:
    """Root game dashboard AppView."""

    idx: ClassVar[int] = 0
    menu_option: ClassVar[str] = "Статус"
    icon: ClassVar[str] = "house"
    roles: ClassVar[tuple[str, ...]] = (Roles.root,)

    def __init__(self) -> None:
        self.state: _ViewState | None = None

    def check_view_data(self) -> bool:
        """Check if data for this view is already fetched.

        Returns:
            bool: True if data is already fetched.
        """
        state: RootState = st.session_state.game


    @fetch_spinner()
    def fetch_data(self) -> None:
        pass

    def render(self) -> None:
        """Render view."""

        self.state = _cache_view_state(**cycle.dict())

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
