from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

import pandas as pd
import streamlit as st
from millify import millify

from egame179_frontend.api.user import UserRoles
from egame179_frontend.settings import settings
from egame179_frontend.state import PlayerState
from egame179_frontend.views.registry import AppView, appview


@dataclass
class _ViewData:
    name: str
    cycle: int
    cycle_start: datetime | None
    balance: str
    balance_delta: str | None
    balances: list[float]
    cycle_params: dict[str, float]
    transactions: pd.DataFrame


@st.cache_data(max_entries=1)
def _cache_view_data(
    name: str,
    cycle: int,
    cycle_start: datetime | None,
    balances: list[float],
    cycle_params: dict[str, float | int],
    transactions: list[dict[str, Any]],
) -> _ViewData:
    transactions_df = pd.DataFrame(reversed(transactions)).drop("user", axis=1)
    init_bal = transactions_df.iloc[-1]["amount"]
    balances = [init_bal] + balances
    balance_delta = millify(balances[-2] - balances[-3], precision=3) if cycle > 1 else None
    return _ViewData(
        name=name,
        cycle=cycle,
        cycle_start=cycle_start,
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
            cycle=state.cycle.id,
            cycle_start=state.cycle.ts_start,
            balances=state.balances,
            cycle_params=state.cycle.dict(),
            transactions=state.transactions,
        )

        st.markdown(f"## Сводный отчёт {view_data.name} Inc.")
        self._metrics_block(view_data)
        self._overview_block(view_data)
        st.markdown("---")
        self._transactions_block(view_data)

    def _metrics_block(self, view_data: _ViewData) -> None:
        if view_data.cycle_start is not None:
            est_timedelta = timedelta(seconds=settings.estimated_cycle_time)
            cycle_start = view_data.cycle_start.time().isoformat()
            cycle_end = (view_data.cycle_start + est_timedelta).time().isoformat()
        else:
            cycle_start = None
            cycle_end = None
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        with col1:
            st.metric("Баланс", value=view_data.balance, delta=view_data.balance_delta)
        with col2:
            st.metric("Цикл #", value=view_data.cycle)
        with col3:
            st.metric("Начался", value=cycle_start)
        with col4:
            st.metric("Ожидаемое время завершения", value=cycle_end)

    def _overview_block(self, view_data: _ViewData) -> None:
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown("#### Динамика баланса")
            # TODO: change to ECharts bar chart
            st.bar_chart(
                data={"cycle": list(range(view_data.cycle + 1)), "balance": view_data.balances},
                x="cycle",
                y="balance",
            )
        with col2:
            st.markdown("#### Параметры цикла")
            st.write("Операционные расходы: ", view_data.cycle_params["alpha"])
            st.write("Комиссия за операции на рынке: ", view_data.cycle_params["beta"])
            st.write("Стоимость складского хранения: ", view_data.cycle_params["gamma"])
            st.write("Время полной поставки: ", view_data.cycle_params["tau_s"])
            st.write("Кредитная ставка за овердрафт: ", view_data.cycle_params["overdraft_rate"])

    def _transactions_block(self, view_data: _ViewData) -> None:
        st.markdown("### Транзакции по корпоративному счёту")
        st.dataframe(view_data.transactions)
