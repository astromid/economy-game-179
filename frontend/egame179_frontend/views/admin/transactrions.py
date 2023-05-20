import itertools
import math
from dataclasses import dataclass
from typing import Any

import pandas as pd
import streamlit as st
from millify import millify

from egame179_frontend.api.user import UserRoles
from egame179_frontend.state import RootState
from egame179_frontend.views.registry import AppView, appview

MAX_METRICS_IN_ROW = 5


@dataclass
class _ViewData:
    cycle: dict[str, Any]
    balances: dict[int, list[float]]
    transactions: pd.DataFrame
    names: dict[int, str]


@st.cache_data(max_entries=1)
def _cache_view_data(
    cycle: dict[str, Any],
    balances: dict[int, list[float]],
    transactions: list[dict[str, Any]],
    names: dict[int, str],
) -> _ViewData:
    transactions_df = pd.DataFrame(reversed(transactions))
    transactions_df["user"] = transactions_df["user"].map(names)
    return _ViewData(
        cycle=cycle,
        balances=balances,
        transactions=transactions_df,
        names=names
    )


@appview
class RootTransactionsView(AppView):
    """Player overview dashboard AppView."""

    idx = 4
    name = "Балансы и транзакции"
    icon = "cash-stack"
    roles = (UserRoles.ROOT.value,)

    def render(self) -> None:
        """Render view."""
        state: RootState = st.session_state.game
        view_data = _cache_view_data(
            cycle=state.cycle.dict(),
            balances=state.balances,
            transactions=state.transactions,
            names=state.names,
        )

        st.markdown("## Балансы и транзакции")
        self._balances_block(view_data)
        self._balcharts_block(view_data)
        st.markdown("---")
        self._transactions_block(view_data)

    def _balances_block(self, view_data: _ViewData) -> None:
        balances = view_data.balances
        n_rows = math.ceil(len(balances) / MAX_METRICS_IN_ROW)
        columns = itertools.chain(*[st.columns(MAX_METRICS_IN_ROW) for _ in range(n_rows)])
        for col, u_id in zip(columns, balances):
            with col:
                ubalances = [1000000] + balances[u_id]
                ubalance_delta = ubalances[-2] - ubalances[-3] if view_data.cycle["id"] > 1 else None
                st.metric(
                    f"Баланс {view_data.names[u_id]}",
                    value=millify(ubalances[-1], precision=2),
                    delta=millify(ubalance_delta, precision=2) if ubalance_delta is not None else None,
                )

    def _balcharts_block(self, view_data: _ViewData) -> None:
        balances = view_data.balances
        n_rows = math.ceil(len(balances) / MAX_METRICS_IN_ROW)
        columns = itertools.chain(*[st.columns(MAX_METRICS_IN_ROW) for _ in range(n_rows)])
        for col, u_id in zip(columns, balances):
            with col:
                ubalances = [1000000] + balances[u_id]
                st.bar_chart(
                    data={
                        "balance": ubalances,
                        "cycle": list(range(view_data.cycle["id"] + 1)),
                    },
                    x="cycle",
                    y="balance",
                )

    def _transactions_block(self, view_data: _ViewData) -> None:
        st.markdown("### Транзакции по корпоративному счетам")
        st.dataframe(view_data.transactions)
