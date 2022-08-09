from dataclasses import dataclass
from types import MappingProxyType

import streamlit as st
from millify import millify
from streamlit_echarts import st_pyecharts

from egame179_frontend.api.models import PlayerState
from egame179_frontend.visualization import barchart

CHART_SIZE = MappingProxyType({"width": 768, "height": 480})


@dataclass
class _ViewState:
    cycle: int
    balance: str
    balance_delta: str | None
    balance_history: list[float]


def overview() -> None:
    """Entry point for the overview page."""
    state: PlayerState = st.session_state.game_state
    view_state = _cache_view_data(
        cycle=state.cycle,
        balance=state.balance[-1],
        balance_prev=state.balance[-2] if len(state.balance) > 2 else None,
        balance_history=state.balance,
    )
    _render_view(view_state)


@st.experimental_memo
def _cache_view_data(
    cycle: int,
    balance: float,
    balance_prev: float | None,
    balance_history: list[float],
) -> _ViewState:
    balance_delta = millify(balance - balance_prev) if balance_prev is not None else None
    return _ViewState(
        cycle=cycle,
        balance=millify(balance),
        balance_delta=balance_delta,
        balance_history=balance_history,
    )


def _render_view(state: _ViewState) -> None:
    hcol1, hcol2, hcol3 = st.columns(3)
    with hcol1:
        st.metric(label="Цикл", value=state.cycle)
    with hcol2:
        st.metric(label="Баланс", value=state.balance, delta=state.balance_delta)
    with hcol3:
        if st.button("Обновить данные"):
            st.experimental_rerun()

    st_pyecharts(
        barchart(
            x_values=list(range(state.cycle)),
            y_values=state.balance_history,
            name="Баланс",
        ),
    )
