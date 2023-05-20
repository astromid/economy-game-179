import math
from dataclasses import dataclass
from itertools import chain
from typing import Any

import pandas as pd
import streamlit as st

from egame179_frontend.api.user import UserRoles
from egame179_frontend.state import RootState
from egame179_frontend.views.registry import AppView, appview

MAX_METRICS_IN_ROW = 5


@dataclass
class _ViewData:
    cycle: int
    prices: dict[int, tuple[float, str | None]]
    storage: dict[int, int]
    supplies: list[dict[str, Any]]
    m_id2name: dict[int, str]
    name2m_id: dict[str, int]
    names: dict[int, str]


@st.cache_data(max_entries=1)
def _cache_view_data(
    cycle: dict[str, Any],
    prices: pd.DataFrame,
    storage: dict[int, int],
    supplies: list[dict[str, Any]],
    m_id2name: dict[int, str],
    names: dict[int, str],
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
        cycle=cycle["id"],
        prices=prices_dict,
        storage=storage,
        supplies=supplies,
        m_id2name=m_id2name,
        name2m_id={market: m_id for m_id, market in m_id2name.items()},
        names=names,
    )


@appview
class RootSuppliesView(AppView):
    """Supplies AppView."""

    idx = 4
    name = "Склады и поставки"
    icon = "box-seam"
    roles = (UserRoles.ROOT.value,)

    def render(self) -> None:
        """Render view."""
        state: RootState = st.session_state.game
        view_data = _cache_view_data(
            cycle=state.cycle.dict(),
            prices=state.prices,
            storage=state.total_storage,
            supplies=state.supplies,
            m_id2name={node_id: node["name"] for node_id, node in state.markets.nodes.items()},
            names=state.names,
        )

        st.markdown("## Поставки")
        _prices_block(prices=view_data.prices, m_id2name=view_data.m_id2name)
        _storage_block(storage=view_data.storage, m_id2name=view_data.m_id2name)
        st.markdown("---")
        _supplies_block(supplies=view_data.supplies, m_id2name=view_data.m_id2name, names=view_data.names)


def _prices_block(prices: dict[int, tuple[float, str | None]], m_id2name: dict[int, str]) -> None:
    n_rows = math.ceil(len(prices) / MAX_METRICS_IN_ROW)
    st.markdown("#### Рыночные цены продажи")
    columns = chain(*[st.columns(MAX_METRICS_IN_ROW) for _ in range(n_rows)])
    for col, m_id in zip(columns, prices):
        with col:
            st.metric(label=m_id2name[m_id], value=prices[m_id][0], delta=prices[m_id][1])


def _storage_block(storage: dict[int, int], m_id2name: dict[int, str]) -> None:
    n_rows = math.ceil(len(storage) / MAX_METRICS_IN_ROW)
    st.markdown("#### Запасы на складах")
    columns = chain(*[st.columns(MAX_METRICS_IN_ROW) for _ in range(n_rows)])
    for col, m_id in zip(columns, storage):
        with col:
            st.metric(label=m_id2name[m_id], value=storage.get(m_id, 0))
    storage_sum = sum(storage.values())
    st.write(f"Суммарное количество товаров на складе: {storage_sum} шт.")


def _supplies_block(
    supplies: list[dict[str, Any]],
    m_id2name: dict[int, str],
    names: dict[int, str],
) -> None:
    st.write("#### Активные поставки")
    for supply in supplies:
        user = names[supply["user"]]
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
        text = f"{ts_start} {user} : >>> {total} шт. {market} [{status}]"
        st.progress(percent, text)
    if not supplies:
        st.info("Нет активных поставок.")
