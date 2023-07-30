import math
from dataclasses import dataclass
from itertools import chain
from time import sleep
from typing import Any

import pandas as pd
import streamlit as st
from httpx import HTTPStatusError

from egame179_frontend.api import SupplyAPI
from egame179_frontend.api.user import UserRoles
from egame179_frontend.state import PlayerState
from egame179_frontend.views.registry import AppView, appview

MAX_METRICS_IN_ROW = 5


@dataclass
class _ViewData:
    player_name: str
    cycle: int
    balance: float
    prices: dict[int, tuple[float, str | None]]
    storage: dict[int, int]
    supplies: list[dict[str, Any]]
    m_id2name: dict[int, str]
    name2m_id: dict[str, int]
    beta: float
    gamma: float


@st.cache_data(max_entries=1)
def _cache_view_data(
    player_name: str,
    cycle: dict[str, Any],
    balance: float,
    prices: pd.DataFrame,
    storage: dict[int, int],
    supplies: list[dict[str, Any]],
    m_id2name: dict[int, str],
    fee_mods: dict[str, float],
) -> _ViewData:
    prices = prices.drop("buy", axis=1)
    prices = prices[prices["cycle"] >= cycle["id"] - 1].sort_values(["market", "cycle"])
    prices["sell_prev"] = prices.groupby("market")["sell"].shift(1)
    prices["sell_delta_pct"] = (prices["sell"] - prices["sell_prev"]) / prices["sell_prev"]
    prices = prices[prices["cycle"] == cycle["id"]].set_index("market")
    prices_delta_dict = prices["sell_delta_pct"].to_dict()
    prices_dict = {
        m_id: (
            price,
            None if pd.isna(prices_delta_dict[m_id]) else f"{prices_delta_dict[m_id]:.2%}",
        )
        for m_id, price in prices["sell"].to_dict().items()
    }
    return _ViewData(
        player_name=player_name,
        cycle=cycle["id"],
        balance=balance,
        prices=prices_dict,
        storage=storage,
        supplies=supplies,
        m_id2name=m_id2name,
        name2m_id={market: m_id for m_id, market in m_id2name.items()},
        beta=cycle["beta"] * fee_mods.get("beta", 1),
        gamma=cycle["gamma"] * fee_mods.get("gamma", 1),
    )


@appview
class SuppliesView(AppView):
    """Supplies AppView."""

    idx = 13
    name = "Склады и поставки"
    icon = "box-seam"
    roles = (UserRoles.PLAYER.value,)

    def render(self) -> None:
        """Render view."""
        state: PlayerState = st.session_state.game
        view_data = _cache_view_data(
            player_name=st.session_state.user.name,
            cycle=state.cycle.dict(),
            balance=state.balances[-1],
            prices=state.prices,
            storage=state.storage,
            supplies=state.supplies,
            m_id2name={node_id: node["name"] for node_id, node in state.markets.nodes.items()},
            fee_mods=state.modificators,
        )

        st.markdown(f"## Поставки {view_data.player_name} Inc.")
        balance_col, _ = st.columns([2, 5])
        with balance_col:
            st.metric(label="Баланс", value=view_data.balance)
        _prices_block(prices=view_data.prices, m_id2name=view_data.m_id2name)
        _storage_block(storage=view_data.storage, m_id2name=view_data.m_id2name, gamma=view_data.gamma)
        st.markdown("---")
        col1, col2 = st.columns([2, 3])
        with col1:
            _supply_form_block(
                storage=view_data.storage,
                m_id2name=view_data.m_id2name,
                name2m_id=view_data.name2m_id,
                beta=view_data.beta,
            )
        with col2:
            _supplies_block(supplies=view_data.supplies, m_id2name=view_data.m_id2name)


def _prices_block(prices: dict[int, tuple[float, str | None]], m_id2name: dict[int, str]) -> None:
    n_rows = math.ceil(len(prices) / MAX_METRICS_IN_ROW)
    st.markdown("#### Рыночные цены продажи")
    columns = chain(*[st.columns(MAX_METRICS_IN_ROW) for _ in range(n_rows)])
    for col, m_id in zip(columns, prices):
        with col:
            st.metric(label=m_id2name[m_id], value=prices[m_id][0], delta=prices[m_id][1])


def _storage_block(storage: dict[int, int], m_id2name: dict[int, str], gamma: float) -> None:
    n_rows = math.ceil(len(storage) / MAX_METRICS_IN_ROW)
    st.markdown("#### Запасы на складе")
    columns = chain(*[st.columns(MAX_METRICS_IN_ROW) for _ in range(n_rows)])
    for col, m_id in zip(columns, storage):
        with col:
            st.metric(label=m_id2name[m_id], value=storage.get(m_id, 0))
    storage_sum = sum(storage.values())
    st.write(f"Суммарное количество товаров на складе: {storage_sum} шт.")
    st.write(f"Ожидаемые расходы на хранение в этом цикле: {storage_sum} шт. x {gamma} = {storage_sum * gamma}")


def _supply_form_block(
    storage: dict[int, int],
    m_id2name: dict[int, str],
    name2m_id: dict[str, int],
    beta: float,
) -> None:
    st.markdown("#### Поставка товаров")
    chosen_market = st.selectbox(
        "Рынок [из доступных на складе]",
        options=[m_id2name[m_id] for m_id in storage if storage[m_id] > 0],
        disabled=st.session_state.interim_block,
    )
    if chosen_market is not None:
        chosen_id = name2m_id[chosen_market]
        amount: int = st.slider(
            "Количество товаров",
            min_value=0,
            max_value=storage[chosen_id],
            value=0,
            disabled=st.session_state.interim_block,
        )
        st.text(f"Комиссия за операцию на рынке: {beta}")
        if st.button("Оформить поставку", disabled=st.session_state.interim_block or amount == 0):
            _make_supply(amount=amount, market_id=chosen_id, market=chosen_market)


def _make_supply(amount: int, market_id: int, market: str) -> None:
    try:
        SupplyAPI.new(market=market_id, quantity=amount)
    except HTTPStatusError as exc:
        st.error(f"Ошибка: {exc = }", icon="⚙")
    else:
        st.success(f"Создана поставка {amount} шт. товаров {market}.", icon="⚙")
        st.session_state.game.clear_after_supply()
    sleep(1.5)
    st.experimental_rerun()


def _supplies_block(supplies: list[dict[str, Any]], m_id2name: dict[int, str]) -> None:
    st.write("#### Активные поставки")
    for supply in supplies:
        total = supply["quantity"]
        market = m_id2name[supply["market"]]
        ts_start = supply["ts_start"].time().strftime("%H:%M:%S")
        if supply["ts_finish"] is None:
            delivered = supply["delivered"]
            percent = delivered / total
            status = f"в процессе: {delivered}/{total}"
        else:
            sold = supply["sold"]
            percent = sold / total
            status = f"закончена, продано: {sold}/{total}"
        text = f"{ts_start} Поставка {total} шт. {market} [{status}]"
        st.progress(percent, text)
    if not supplies:
        st.info("Нет активных поставок.")
