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

    def render(self) -> None:
        """Render view."""
        state: PlayerState = st.session_state.game
        view_data = _cache_view_data(
            name=st.session_state.user.name,
            cycle=state.cycle.cycle,
            balances=state.balances,
            cycle_params=state.cycle_params,
            transactions=state.transactions,
        )

        st.markdown(f"## Сводный отчёт {view_data.name} Inc.")
        self._metrics_block(view_data)
        self._overview_block(view_data)
        st.markdown("---")
        self._transactions_block(view_data)

    def _metrics_block(self, view_data: _ViewData) -> None:
        col1, col2, _ = st.columns([1, 1, 5])
        with col1:
            st.metric(label="Цикл", value=view_data.cycle)
        with col2:
            st.metric(label="Баланс", value=view_data.balance, delta=view_data.balance_delta)
        if st.session_state.interim_block:
            st.warning("Цикл ещё не запущен. Активные элементы управления заблокированы.", icon="⚠️")

    def _overview_block(self, view_data: _ViewData) -> None:
        col1, col2 = st.columns([1, 1])
        with col1:
            # TODO: change to ECharts bar chart
            st.bar_chart(
                data={"cycle": list(range(1, view_data.cycle + 1)), "balance": view_data.balances},
                x="cycle",
                y="balance",
            )
        with col2:
            st.markdown("#### Параметры цикла")
            st.write("Операционные расходы: ", view_data.cycle_params["alpha"])
            st.write("Комиссия за операции на рынке: ", view_data.cycle_params["beta"])
            st.write("Стоимость складского хранения: ", view_data.cycle_params["gamma"])
            st.write("Время полной поставки: ", view_data.cycle_params["tau_s"])

    def _transactions_block(self, view_data: _ViewData) -> None:
        st.markdown("### Транзакции по корпоративному счёту")
        st.dataframe(view_data.transactions)
