from dataclasses import dataclass
from itertools import chain

import pandas as pd
import streamlit as st

from egame179_frontend.api.models import PlayerState

MAX_MARKETS_IN_ROW = 5


@dataclass
class _BuyMarketStatus:
    buy_price: str
    buy_price_delta: str | None
    buy_history: list[float]
    theta: float


@dataclass
class _ViewState:
    cycle: int
    markets: dict[str, _BuyMarketStatus]
    markets_df: pd.DataFrame


def manufacturing() -> None:
    state: PlayerState = st.session_state.game_state
    view_state = _cache_view_data(
        cycle=state.cycle,
        markets_buy=state.markets_buy,
        markets_sell=state.markets_sell,
        markets_top=state.markets_top,
    )
    _render_view(view_state)


@st.experimental_memo
def _cache_view_data(
    cycle: int,
    markets_buy: dict[str, list[float]],
    markets_sell: dict[str, list[float]],
    markets_top: dict[str, dict[str, float | None]],
) -> _ViewState:

    return _ViewState(
        cycle=cycle,
    )


def _render_view(state: _ViewState) -> None:
    markets = state.markets

    n_rows = len(markets) // MAX_MARKETS_IN_ROW + 1
    if len(resources) % MAX_MARKETS_IN_ROW:
        n_rows -= 1

    st.markdown("## Производство")
    columns = chain(*[st.columns(MAX_MARKETS_IN_ROW) for _ in range(n_rows)])
    for col, res in zip(columns, resources):
        with col:
            st.metric(
                label=res,
                value=resources[res]["price"],
                delta=f"{resources[res]['delta']:.2%}",
            )

    with st.form("manufacturing_form"):
        market = st.selectbox("Целевой рынок", list(st.session_state.game_state.resources.keys()))
        volume = st.slider("Количество товаров", min_value=0, max_value=100)

        total_price = st.session_state.game_state.resources[market]["price"] * volume
        rest_balance = st.session_state.game_state.balance - total_price

        st.text(f"Цена производства: {total_price}, остаток баланса: {rest_balance}")
        st.form_submit_button("Отправить на производство", on_click=manufacturing_callback)
