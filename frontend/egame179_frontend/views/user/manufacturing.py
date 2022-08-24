from dataclasses import dataclass
from itertools import chain
from math import ceil
from types import MappingProxyType

import streamlit as st
from millify import millify
from streamlit_echarts import st_pyecharts

from egame179_frontend.api.mock import mock_manufacturing
from egame179_frontend.api.models import PlayerState
from egame179_frontend.visualization import radar_chart

MAX_METRICS_IN_ROW = 5
X_AXIS = "cycle"
Y_AXIS = "price"
C_AXIS = "market"
CHART_SIZE = MappingProxyType({"width": 1000, "height": 600})


def manufacturing(state: PlayerState) -> None:
    """Entry point for manufacturing view.

    Args:
        state (PlayerState): PlayerState object.
    """
    view_state = _cache_view_data(
        cycle=state.cycle,
        balance=state.player.balances[-1],
        markets_buy={market: m_state.buy for market, m_state in state.markets.items()},
        thetas={market: pm_info.theta for market, pm_info in state.player.products.items()},
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
    n_rows: int


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
    return _ViewState(
        cycle=cycle,
        balance=balance,
        markets=markets,
        n_rows=ceil(len(markets) / MAX_METRICS_IN_ROW),
    )


def _render_view(state: _ViewState) -> None:
    st.markdown("## Производство")
    _prices_block(
        n_rows=state.n_rows,
        markets=state.markets,
    )
    col1, col2 = st.columns([2, 3])
    with col1:
        _buy_form_block(markets=state.markets, balance=state.balance)
    with col2:
        _theta_radar_block(markets=state.markets)


def _prices_block(n_rows: int, markets: dict[str, _BuyMarketStatus]) -> None:
    st.markdown("### Закупочные цены")
    columns = chain(*[st.columns(MAX_METRICS_IN_ROW) for _ in range(n_rows)])
    for col, (market, market_status) in zip(columns, markets.items()):
        with col:
            st.metric(label=market, value=market_status.price, delta=market_status.price_delta_pct)


def _buy_form_block(markets: dict[str, _BuyMarketStatus], balance: float) -> None:
    st.markdown("### Производство товаров")
    chosen_market: str = st.selectbox("Целевой рынок", list(markets.keys()))
    real_price = (1 - markets[chosen_market].theta) * markets[chosen_market].price_history[-1]
    real_price = round(real_price, 2)
    max_volume = int(balance // real_price)
    volume: int = st.slider("Количество товаров", min_value=0, max_value=max_volume)  # type: ignore

    expense = volume * real_price
    rest_balance = round(balance - expense, 2)

    st.text(f"Цена закупки с учетом скидки: {real_price}")
    st.text(f"Расходы: {volume} шт. x {real_price} = {expense}")
    st.text(f"Остаток баланса: {rest_balance}")
    if st.button("Произвести"):
        _manufacturing(volume=volume, market=chosen_market)


def _manufacturing(volume: int, market: str) -> None:
    status = False
    if volume > 0:
        with st.spinner("Отправка на производство..."):
            status = mock_manufacturing(volume=volume, market=market)
    if status:
        st.success(f"{volume} шт. товаров {market} отправлены на склад.", icon="⚙")
    else:
        st.error("Ошибка отправки на производство.", icon="⚙")


def _theta_radar_block(markets: dict[str, _BuyMarketStatus]) -> None:
    st.markdown("### Эффективность производства")
    st_pyecharts(
        radar_chart(thetas={market: market_status.theta for market, market_status in markets.items()}),
        height="500px",
    )
