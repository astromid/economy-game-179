from dataclasses import dataclass
from itertools import chain
from math import ceil

import streamlit as st
from millify import millify

from egame179_frontend.api.models import PlayerState

MAX_MARKETS_IN_ROW = 5


def manufacturing() -> None:
    """Entry point for manufacturing view."""
    state: PlayerState = st.session_state.game_state
    view_state = _cache_view_data(
        cycle=state.cycle,
        balance=state.balance[-1],
        markets_buy=state.markets_buy,
        thetas=state.thetas,
    )
    _render_view(view_state)


@dataclass
class _BuyMarketStatus:
    price: str
    price_delta_pct: str | None
    price_history: list[float]
    theta: float


@dataclass
class _ViewState:
    cycle: int
    balance: float
    markets: dict[str, _BuyMarketStatus]


@st.experimental_memo
def _cache_view_data(
    cycle: int,
    balance: float,
    markets_buy: dict[str, list[float]],
    thetas: dict[str, float],
) -> _ViewState:
    markets: dict[str, _BuyMarketStatus] = {}
    for market, prices in markets_buy.items():
        price_delta_pct = None
        if cycle > 1:
            *_, price_prev, price = prices
            price_delta_pct = (price - price_prev) / price_prev
        markets[market] = _BuyMarketStatus(
            price=millify(prices[-1]),
            price_delta_pct=f"{price_delta_pct:.2%}" if price_delta_pct is not None else None,
            price_history=prices,
            theta=thetas[market],
        )
    return _ViewState(cycle=cycle, balance=balance, markets=markets)


def _render_view(state: _ViewState) -> None:
    markets = state.markets
    n_rows = ceil(len(markets) / MAX_MARKETS_IN_ROW)

    st.markdown("## Производство")
    columns = chain(*[st.columns(MAX_MARKETS_IN_ROW) for _ in range(n_rows)])
    for col, (market, market_status) in zip(columns, markets.items()):
        with col:
            st.metric(
                label=market,
                value=market_status.price,
                delta=market_status.price_delta_pct,
            )

    with st.form("manufacturing_form"):
        chosen_market: str = st.selectbox("Целевой рынок", list(markets.keys()))
        real_price = (1 - markets[chosen_market].theta) * markets[chosen_market].price_history[-1]
        max_volume = int(state.balance // real_price)
        volume: int = st.slider("Количество товаров", min_value=0, max_value=max_volume)  # type: ignore

        expense = volume * real_price
        rest_balance = state.balance - expense

        st.text(f"Расходы: {expense}, остаток баланса: {rest_balance}")
        st.form_submit_button("Отправить на производство", on_click=_manufacturing_callback)


def _manufacturing_callback() -> None:
    st.write("Отправляем на производство...")
