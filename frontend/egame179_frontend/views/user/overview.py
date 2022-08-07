from dataclasses import dataclass

import pandas as pd
import streamlit as st
from millify import millify

from egame179_frontend.api.models import PlayerState
from egame179_frontend.visualization import cycles_history_chart


@dataclass
class _ViewState:
    cycle: int
    balance: str
    balance_delta: str | None
    balance_df: pd.DataFrame
    max_balance: float


def overview() -> None:
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
    balance_df = pd.DataFrame({"balance": balance_history})
    balance_df["cycle"] = balance_df.index
    return _ViewState(
        cycle=cycle,
        balance=millify(balance),
        balance_delta=balance_delta,
        balance_df=balance_df,
        max_balance=max(balance_history),
    )


def _render_view(state: _ViewState) -> None:
    hcol1, hcol2, hcol3 = st.columns(3)
    with hcol1:
        st.metric(label="Цикл", value=state.cycle)
    with hcol2:
        st.metric(label="Баланс", value=state.balance, delta=state.balance_delta)
    with hcol3:
        st.markdown("Page 1 🎉")

    st.markdown("### История баланса")
    st.altair_chart(
        cycles_history_chart(
            state.balance_df,
            x_shorthand="cycle:Q",
            y_shorthand="balance:Q",
            color_shorthand=None,
            max_x=state.cycle,
            max_y=state.max_balance,
            width=1000,
            height=600,
        ),
    )

    with st.sidebar:
        st.markdown("Additional sidebar content")
