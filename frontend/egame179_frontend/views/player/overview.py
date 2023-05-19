from dataclasses import dataclass
from datetime import timedelta
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
    cycle: dict[str, Any]
    balances: list[float]
    transactions: pd.DataFrame
    fee_mods: dict[str, float]


@st.cache_data(max_entries=1)
def _cache_view_data(
    name: str,
    cycle: dict[str, Any],
    balances: list[float],
    transactions: list[dict[str, Any]],
    fee_mods: dict[str, float],
) -> _ViewData:
    transactions_df = pd.DataFrame(reversed(transactions)).drop("user", axis=1)
    init_bal = transactions_df.iloc[-1]["amount"]
    return _ViewData(
        name=name,
        cycle=cycle,
        balances=[init_bal] + balances,
        transactions=transactions_df,
        fee_mods=fee_mods,
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
            cycle=state.cycle.dict(),
            balances=state.balances,
            transactions=state.transactions,
            fee_mods=state.modificators,
        )

        st.markdown(f"## Сводный отчёт {view_data.name} Inc.")
        self._metrics_block(view_data)
        self._overview_block(view_data)
        st.markdown("---")
        self._transactions_block(view_data)

    def _metrics_block(self, view_data: _ViewData) -> None:
        ts_start = view_data.cycle["ts_start"]
        if ts_start is not None:
            est_timedelta = timedelta(seconds=settings.estimated_cycle_time)
            cycle_start = ts_start.time().isoformat()
            cycle_end = (ts_start + est_timedelta).time().isoformat()
        else:
            cycle_start = "Ожидание"
            cycle_end = "Перерыв ~5 минут"
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        with col1:
            balances = view_data.balances
            balance_delta = balances[-2] - balances[-3] if view_data.cycle["id"] > 1 else None
            st.metric(
                "Баланс",
                value=millify(balances[-1], precision=2),
                delta=millify(balance_delta, precision=2) if balance_delta is not None else None,
            )
        with col2:
            st.metric("Цикл #", value=view_data.cycle["id"])
        with col3:
            st.metric("Начался", value=cycle_start)
        with col4:
            st.metric("Ожидаемое время завершения", value=cycle_end)

    def _overview_block(self, view_data: _ViewData) -> None:
        col1, col2 = st.columns([1, 1], gap="medium")
        with col1:
            st.markdown("#### Динамика баланса")
            st.bar_chart(
                data={"cycle": list(range(view_data.cycle["id"] + 1)), "balance": view_data.balances},
                x="cycle",
                y="balance",
            )
        with col2:
            alpha = view_data.cycle["alpha"]
            alpha_coeff = view_data.fee_mods.get("alpha", 1)
            beta = view_data.cycle["beta"]
            beta_coeff = view_data.fee_mods.get("beta", 1)
            gamma = view_data.cycle["gamma"]
            gamma_coeff = view_data.fee_mods.get("gamma", 1)

            st.markdown("#### Параметры цикла")
            st.write(f"Организационные расходы: {alpha * alpha_coeff} ({alpha} x {alpha_coeff})")
            st.write(f"Комиссия за операции на рынке: {beta * beta_coeff} ({beta} x {beta_coeff})")
            st.write(f"Стоимость складского хранения: {gamma * gamma_coeff} ({gamma} x {gamma_coeff})")
            st.write(f"Время полной поставки: {view_data.cycle['tau_s']} с")
            st.write(f"Кредитная ставка за овердрафт: {view_data.cycle['overdraft_rate']}")

    def _transactions_block(self, view_data: _ViewData) -> None:
        st.markdown("### Транзакции по корпоративному счёту")
        st.dataframe(view_data.transactions)
