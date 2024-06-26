import math
from dataclasses import dataclass
from itertools import chain
from time import sleep

import pandas as pd
import streamlit as st
from httpx import HTTPStatusError
from streamlit_echarts import st_pyecharts

from egame179_frontend.api import ProductionAPI
from egame179_frontend.api.user import UserRoles
from egame179_frontend.state import PlayerState
from egame179_frontend.views.registry import AppView, appview
from egame179_frontend.visualization import radar_chart

MAX_METRICS_IN_ROW = 5


@dataclass
class _ViewData:
    player_name: str
    cycle: int
    balance: float
    unlocked_markets: list[int]
    prices: dict[int, tuple[float, str | None]]
    thetas: dict[int, float]
    products: pd.DataFrame
    m_id2name: dict[int, str]
    name2m_id: dict[str, int]


@st.cache_data(max_entries=1)
def _cache_view_data(
    player_name: str,
    cycle: int,
    balance: float,
    unlocked_markets: list[int],
    prices: pd.DataFrame,
    thetas: dict[int, float],
    products: pd.DataFrame,
    m_id2name: dict[int, str],
) -> _ViewData:
    prices = prices.drop("sell", axis=1)
    prices = prices[prices["cycle"] >= cycle - 1].sort_values(["market", "cycle"])
    prices["buy_prev"] = prices.groupby("market")["buy"].shift(1)
    prices["buy_delta_pct"] = (prices["buy"] - prices["buy_prev"]) / prices["buy_prev"]
    prices = prices[prices["cycle"] == cycle].set_index("market")
    prices_delta_dict = prices["buy_delta_pct"].to_dict()
    prices_dict = {
        m_id: (
            price,
            None if pd.isna(prices_delta_dict[m_id]) else f"{prices_delta_dict[m_id]:.2%}",
        )
        for m_id, price in prices["buy"].to_dict().items()
    }
    if not products.empty:
        products["market_name"] = products["market"].map(m_id2name)
    return _ViewData(
        player_name=player_name,
        cycle=cycle,
        balance=balance,
        unlocked_markets=unlocked_markets,
        prices=prices_dict,
        thetas=thetas,
        products=products,
        m_id2name=m_id2name,
        name2m_id={market: m_id for m_id, market in m_id2name.items()},
    )


@appview
class ManufacturingView(AppView):
    """Manufacturing AppView."""

    idx = 12
    name = "Производство"
    icon = "gear"
    roles = (UserRoles.PLAYER.value,)

    def render(self) -> None:  # noqa: WPS213
        """Render view."""
        state: PlayerState = st.session_state.game
        view_data = _cache_view_data(
            player_name=st.session_state.user.name,
            cycle=state.cycle.id,
            balance=state.balances[-1],
            unlocked_markets=state.unlocked_markets,
            prices=state.prices,
            thetas=state.thetas,
            products=pd.DataFrame(state.production),
            m_id2name={node_id: node["name"] for node_id, node in state.markets.nodes.items()},
        )

        st.markdown(f"## Производство {view_data.player_name} Inc.")
        balance_col, _ = st.columns([2, 5])
        with balance_col:
            st.metric(label="Баланс", value=view_data.balance)
        _prices_block(prices=view_data.prices, m_id2name=view_data.m_id2name)

        col1, col2 = st.columns([2, 3])
        with col1:
            _buy_form_block(
                balance=view_data.balance,
                unlocked_markets=view_data.unlocked_markets,
                prices=view_data.prices,
                thetas=view_data.thetas,
                m_id2name=view_data.m_id2name,
                name2m_id=view_data.name2m_id,
            )
        with col2:
            _theta_radar_block(thetas=view_data.thetas, m_id2name=view_data.m_id2name)
        st.markdown("---")
        st.markdown("### Записи о производстве")
        if view_data.products.empty:
            st.write("Нет записей о производстве.")
        else:
            products = view_data.products.copy()
            products["market"] = products["market"].map(view_data.m_id2name)
            st.dataframe(products[["id", "ts", "cycle", "quantity", "market"]])


def _prices_block(prices: dict[int, tuple[float, str | None]], m_id2name: dict[int, str]) -> None:
    n_rows = math.ceil(len(prices) / MAX_METRICS_IN_ROW)
    st.markdown("#### Рыночные цены производства")
    columns = chain(*[st.columns(MAX_METRICS_IN_ROW) for _ in range(n_rows)])
    for col, m_id in zip(columns, prices):
        with col:
            st.metric(label=m_id2name[m_id], value=prices[m_id][0], delta=prices[m_id][1])


def _buy_form_block(
    balance: float,
    unlocked_markets: list[int],
    prices: dict[int, tuple[float, str | None]],
    thetas: dict[int, float],
    m_id2name: dict[int, str],
    name2m_id: dict[str, int],
) -> None:
    st.markdown("#### Производство товаров")
    chosen_market = st.selectbox(
        "Рынок [из доступных]",
        options=[m_id2name[m_id] for m_id in unlocked_markets],
        disabled=st.session_state.interim_block,
    )
    if chosen_market is not None:
        chosen_id = name2m_id[chosen_market]
        real_price = (1 - thetas[chosen_id]) * prices[chosen_id][0]
        max_amount = max(0, int(balance // real_price))
        amount: int = st.slider(
            "Количество товаров",
            min_value=0,
            max_value=max_amount if max_amount > 0 else 1,
            value=0,
            disabled=st.session_state.interim_block or max_amount == 0,
        )
        if max_amount == 0:
            amount = 0
            st.warning("Баланса недостаточно для производства на данном рынке", icon="⚠️")

        expense = amount * real_price
        rest_balance = round(balance - expense, 2)
        st.text(f"Цена производства с учетом скидки: {real_price}")
        st.text(f"Расходы: {amount} шт. x {real_price} = {expense}")
        st.text(f"Остаток баланса: {rest_balance}")
        if st.button("Произвести и отправить на склад", disabled=st.session_state.interim_block or amount == 0):
            _manufacturing(amount=amount, market_id=chosen_id, market=chosen_market)


def _manufacturing(amount: int, market_id: int, market: str) -> None:
    try:
        ProductionAPI.new(market=market_id, quantity=amount)
    except HTTPStatusError as exc:
        st.error(f"Ошибка: {exc = }", icon="⚙")
    else:
        st.success(f"{amount} шт. товаров {market} отправлены на склад.", icon="⚙")
        st.session_state.game.clear_after_buy()
    sleep(1.5)
    st.experimental_rerun()


def _theta_radar_block(thetas: dict[int, float], m_id2name: dict[int, str]) -> None:
    st.markdown("#### Текущая эффективность производства")
    st_pyecharts(
        radar_chart(thetas={m_id2name[m_id]: theta for m_id, theta in thetas.items()}),
        height="500px",
    )
