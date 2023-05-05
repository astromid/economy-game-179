from dataclasses import dataclass
from typing import Any

import pandas as pd
import streamlit as st
from millify import millify

from egame179_frontend.api.user import UserRoles
from egame179_frontend.state.player import PlayerState
from egame179_frontend.views.registry import AppView, appview


@dataclass
class _ViewData:
    name: str
    cycle: int
    balance: str
    balance_delta: str | None
    balances: list[float]
    cycle_params: dict[str, float]
    transactions: pd.DataFrame


@st.cache_data(max_entries=1)
def _cache_view_data(
    name: str,
    cycle: int,
    balances: list[float],
    cycle_params: dict[str, float | int],
    transactions: list[dict[str, Any]],
) -> _ViewData:
    balance_delta = millify(balances[-1] - balances[-2], precision=3) if cycle > 1 else None
    transactions_df = pd.DataFrame(transactions).drop("user_id", axis=1).sort_values("ts", ascending=False)
    return _ViewData(
        name=name,
        cycle=cycle,
        balance=millify(balances[-1], precision=3),
        balance_delta=balance_delta,
        balances=balances,
        cycle_params=cycle_params,
        transactions=transactions_df,
    )


@appview
class PlayerDashboard(AppView):
    """Player overview dashboard AppView."""

    idx = 10
    name = "Сводный отчёт"
    icon = "cash-stack"
    roles = (UserRoles.PLAYER.value,)

    def __init__(self) -> None:
        self.view_data: _ViewData | None = None

    def render(self) -> None:
        """Render view."""
        self.view_data = self._cache_view_data(st.session_state.game)

        st.markdown(f"## Сводный отчёт {self.view_data.name} Inc.")
        col01, col02, _ = st.columns([1, 2, 5])
        with col01:
            st.metric(label="Цикл", value=self.view_data.cycle)
        with col02:
            st.metric(label="Баланс", value=self.view_data.balance, delta=self.view_data.balance_delta)

        col11, col12 = st.columns([1, 1])
        with col11:
            # TODO: change to ECharts bar chart
            st.bar_chart(
                data={
                    "cycle": list(range(1, self.view_data.cycle + 1)),
                    "balance": self.view_data.balances,
                },
                x="cycle",
                y="balance",
            )
        with col12:
            st.write(self.view_data.cycle_params)

        st.markdown("---")
        st.markdown("### Транзакции по корпоративному счёту")
        st.dataframe(self.view_data.transactions)

    def _cache_view_data(self, state: PlayerState) -> _ViewData:
        return _cache_view_data(
            name=st.session_state.user.name,
            cycle=state.cycle.cycle,
            balances=state.balances,
            cycle_params=state.cycle_params,
            transactions=state.transactions,
        )
