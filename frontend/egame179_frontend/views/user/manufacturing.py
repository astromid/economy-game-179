from dataclasses import dataclass
from itertools import chain
from math import ceil
from types import MappingProxyType

import pandas as pd
import streamlit as st
from millify import millify
from streamlit_echarts import st_pyecharts

from egame179_frontend.api.models import PlayerState
from egame179_frontend.visualization import radar_chart, stocks_chart

MAX_MARKETS_IN_ROW = 5
X_AXIS = "cycle"
Y_AXIS = "price"
C_AXIS = "market"
CHART_SIZE = MappingProxyType({"width": 1000, "height": 600})


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
    prices_df: pd.DataFrame


@st.experimental_memo  # type: ignore
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
            price=millify(prices[-1], precision=3),
            price_delta_pct=f"{price_delta_pct:.2%}" if price_delta_pct is not None else None,
            price_history=prices,
            theta=thetas[market],
        )
    prices_df = pd.DataFrame(markets_buy)
    prices_df[X_AXIS] = prices_df.index + 1
    return _ViewState(
        cycle=cycle,
        balance=balance,
        markets=markets,
        prices_df=prices_df.melt(id_vars=X_AXIS, var_name=C_AXIS, value_name=Y_AXIS),
    )


def _render_view(state: _ViewState) -> None:
    st.markdown("## Производство")
    _prices_block(
        n_rows=ceil(len(state.markets) / MAX_MARKETS_IN_ROW),
        markets=state.markets,
    )
    col1, col2 = st.columns(2)
    with col1:
        _buy_form_block(markets=state.markets, balance=state.balance)
    with col2:
        _theta_radar_block(markets=state.markets)
    # _prices_history_block(state.prices_df)


def _prices_block(n_rows: int, markets: dict[str, _BuyMarketStatus]) -> None:
    st.markdown("### Закупочные цены")
    columns = chain(*[st.columns(MAX_MARKETS_IN_ROW) for _ in range(n_rows)])
    for col, (market, market_status) in zip(columns, markets.items()):
        with col:
            st.metric(
                label=market,
                value=market_status.price,
                delta=market_status.price_delta_pct,
            )


def _buy_form_block(markets: dict[str, _BuyMarketStatus], balance: float) -> None:
    st.markdown("### Производство товаров")
    chosen_market: str = st.selectbox("Целевой рынок", list(markets.keys()))
    real_price = (1 - markets[chosen_market].theta) * markets[chosen_market].price_history[-1]
    max_volume = int(balance // real_price)
    volume: int = st.slider("Количество товаров", min_value=0, max_value=max_volume)  # type: ignore

    expense = volume * real_price
    rest_balance = balance - expense

    st.text(f"Расходы: {expense}, остаток баланса: {rest_balance}")
    if st.button("Произвести"):
        st.success(f"{volume} шт. товаров {chosen_market} отправлены на склад.", icon="✅")


def _theta_radar_block(markets: dict[str, _BuyMarketStatus]) -> None:
    st.markdown("### Эффективность производства")
    st_pyecharts(
        radar_chart(thetas={market: market_status.theta for market, market_status in markets.items()}),
        height="500px",
    )


def _prices_history_block(prices_df: pd.DataFrame) -> None:
    with st.expander("История закупочных цен"):
        st.altair_chart(
            stocks_chart(
                prices_df,
                x_shorthand=f"{X_AXIS}:Q",
                y_shorthand=f"{Y_AXIS}:Q",
                color_shorthand=f"{C_AXIS}:N",
                chart_size=CHART_SIZE,  # type: ignore
            ),
        )
