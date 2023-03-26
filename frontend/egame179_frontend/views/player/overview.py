from dataclasses import dataclass
from types import MappingProxyType
from typing import ClassVar

import streamlit as st
from millify import millify

from egame179_frontend.api.user import UserRoles
from egame179_frontend.state.state import PlayerState
from egame179_frontend.views.registry import appview

CHART_SIZE = MappingProxyType({"width": 768, "height": 480})


@dataclass
class _ViewData:
    cycle: int
    balance: str
    balance_delta: str | None
    balance_history: list[float]
    name: str


@st.cache_data(max_entries=1)
def _cache_view_data(cycle: int, balance_history: list[float], name: str) -> _ViewData:
    balance_delta = None
    if cycle > 1:
        *_, balance_prev, balance = balance_history
        balance_delta = balance - balance_prev
    return _ViewData(
        cycle=cycle,
        balance=millify(balance_history[-1], precision=3),
        balance_delta=millify(balance_delta, precision=3) if balance_delta is not None else None,
        balance_history=balance_history,
        name=name,
    )


@appview
class PlayerDashboard:
    """Player overview dashboard AppView."""

    idx: ClassVar[int] = 0
    name: ClassVar[str] = "Обзор"
    icon: ClassVar[str] = "house"
    roles: ClassVar[tuple[str, ...]] = (UserRoles.PLAYER.value,)

    def __init__(self) -> None:
        self.state: _ViewData | None = None

    def fetch_api_data(self) -> None:
        """Fetch data for this view."""

    def render(self) -> None:
        """Render view."""
        game_state: PlayerState = st.session_state.game
        self.state = _cache_view_data(cycle=state.cycle, balance_history=state.player.balances, name=state.player.name)
        hcol1, hcol2, *_ = st.columns(5)
        with hcol1:
            st.metric(label="Цикл", value=state.cycle)
        with hcol2:
            st.metric(label="Баланс", value=state.balance, delta=state.balance_delta)

        st.markdown(f"### История баланса {state.name} Inc.")
        bcol1, _ = st.columns(2)
        with bcol1:
            st.bar_chart(
                data={"cycle": list(range(1, state.cycle + 1)), "balance": state.balance_history},
                x="cycle",
                y="balance",
            )
