from dataclasses import dataclass
from types import MappingProxyType

import streamlit as st
from millify import millify

from egame179_frontend.api.models import PlayerState

CHART_SIZE = MappingProxyType({"width": 768, "height": 480})


def overview(state: PlayerState) -> None:
    """Entry point for the overview page.

    Args:
        state (PlayerState): PlayerState object.
    """
    view_state = _cache_view_data(cycle=state.cycle, balance_history=state.player.balances)
    _render_view(view_state)


@dataclass
class _ViewState:
    cycle: int
    balance: str
    balance_delta: str | None
    balance_history: list[float]


@st.experimental_memo  # type: ignore
def _cache_view_data(cycle: int, balance_history: list[float]) -> _ViewState:
    balance_delta = None
    if cycle > 1:
        *_, balance_prev, balance = balance_history
        balance_delta = balance - balance_prev
    return _ViewState(
        cycle=cycle,
        balance=millify(balance_history[-1], precision=3),
        balance_delta=millify(balance_delta, precision=3) if balance_delta is not None else None,
        balance_history=balance_history,
    )


def _render_view(state: _ViewState) -> None:
    hcol1, hcol2, *_ = st.columns(5)
    with hcol1:
        st.metric(label="Цикл", value=state.cycle)
    with hcol2:
        st.metric(label="Баланс", value=state.balance, delta=state.balance_delta)

    st.markdown("### История баланса корпорации")
    bcol1, _ = st.columns(2)
    with bcol1:
        st.bar_chart(
            data={"cycle": list(range(1, state.cycle + 1)), "balance": state.balance_history},
            x="cycle",
            y="balance",
        )
