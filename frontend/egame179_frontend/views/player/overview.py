from dataclasses import dataclass

import streamlit as st
from millify import millify

from egame179_frontend.api.user import UserRoles
from egame179_frontend.state.state import PlayerState
from egame179_frontend.views.registry import AppView, appview


@dataclass
class _ViewData:
    cycle: int
    balance: str
    balance_delta: str | None
    balances: list[float]
    name: str


@st.cache_data(max_entries=1)
def _cache_view_data(cycle: int, balances: list[float], name: str) -> _ViewData:
    balance_delta = balances[-1] - balances[-2] if cycle > 1 else None
    return _ViewData(
        cycle=cycle,
        balance=millify(balances[-1], precision=3),
        balance_delta=millify(balance_delta, precision=3) if balance_delta is not None else None,
        balances=balances,
        name=name,
    )


@appview
class PlayerDashboard(AppView):
    """Player overview dashboard AppView."""

    idx = 10
    name = "Обзор"
    icon = "house"
    roles = (UserRoles.PLAYER.value,)

    def __init__(self) -> None:
        self.view_data: _ViewData | None = None

    def render(self) -> None:
        """Render view."""
        state: PlayerState = st.session_state.game
        self.view_data = _cache_view_data(
            cycle=state.cycle.cycle,
            balances=state.balances,
            name=st.session_state.user.name,
        )
        hcol1, hcol2, _ = st.columns([1, 1, 7])
        with hcol1:
            st.metric(label="Цикл", value=self.view_data.cycle)
        with hcol2:
            st.metric(label="Баланс", value=self.view_data.balance, delta=self.view_data.balance_delta)

        st.markdown(f"### История баланса {self.view_data.name} Inc.")
        bcol1, _ = st.columns([1, 2])
        with bcol1:
            st.bar_chart(
                data={
                    "cycle": list(range(1, self.view_data.cycle + 1)),
                    "balance": self.view_data.balances,
                },
                x="cycle",
                y="balance",
            )
