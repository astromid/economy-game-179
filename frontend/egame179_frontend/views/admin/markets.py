from dataclasses import dataclass
from types import MappingProxyType

import networkx as nx
import pandas as pd
import pyecharts as pe
import streamlit as st
from streamlit_echarts import st_pyecharts

from egame179_frontend.api.user import UserRoles
from egame179_frontend.state import RootState
from egame179_frontend.views.registry import AppView, appview
from egame179_frontend.visualization import markets_graph, stocks_chart

X_AXIS = "cycle"
Y_AXIS = "price"
C_AXIS = "market_name"
CHART_SIZE = MappingProxyType({"width": 600, "height": 350})


@dataclass
class _ViewData:
    cycle: int
    markets_graph: pe.charts.Graph
    buy_prices: pd.DataFrame
    sell_prices: pd.DataFrame
    current_prices: pd.DataFrame
    shares: pd.DataFrame


@st.cache_data(max_entries=1)
def _cache_view_data(
    cycle: int,
    _nx_graph: nx.Graph,
    prices: pd.DataFrame,
    shares: dict[tuple[int, int], tuple[int, float | None]],
    names: dict[int, str],
    owner_colors: dict[int, str],
) -> _ViewData:
    market2name = {node_id: node["name"] for node_id, node in _nx_graph.nodes.items()}

    prices["market_name"] = prices["market"].map(market2name)
    current_prices = prices[prices["cycle"] == cycle].copy()
    current_prices = current_prices[["market_name", "buy", "sell"]]

    pe_graph = markets_graph(
        nx_graph=_nx_graph,
        home=0,
        owned=[],
        unlocked=[],
        owner_colors=owner_colors,
    )
    shares_df = pd.DataFrame(
        [
            {
                "market": market2name[market],
                "position": position,
                "company": names[user],
                "share": share,
            }
            for (market, position), (user, share) in shares.items()
        ],
    )
    return _ViewData(
        cycle=cycle,
        markets_graph=pe_graph,
        buy_prices=prices[[X_AXIS, "buy", C_AXIS]].rename(columns={"buy": Y_AXIS}),
        sell_prices=prices[[X_AXIS, "sell", C_AXIS]].rename(columns={"sell": Y_AXIS}),
        current_prices=current_prices,
        shares=shares_df,
    )


@appview
class RootMarketsView(AppView):
    """Markets AppView."""

    idx = 1
    name = "Рынки"
    icon = "pie-chart-fill"
    roles = (UserRoles.ROOT.value,)

    def render(self) -> None:
        """Render view."""
        state: RootState = st.session_state.game
        view_data = _cache_view_data(
            cycle=state.cycle.id,
            _nx_graph=state.detailed_markets,
            prices=state.prices.copy(),
            shares=state.shares,
            names=state.names,
            owner_colors=state.player_colors,
        )

        st.markdown("## Аналитика по рынкам")
        col01, col02 = st.columns([3, 2])
        with col01:
            st_pyecharts(view_data.markets_graph, height="600px")
        with col02:
            st.dataframe(view_data.current_prices, height=600)

        col11, col12 = st.columns(2)
        with col11:
            st.markdown("##### Цены производства")
            st.altair_chart(
                stocks_chart(
                    view_data.buy_prices,
                    x_shorthand=f"{X_AXIS}:Q",
                    y_shorthand=f"{Y_AXIS}:Q",
                    color_shorthand=f"{C_AXIS}:N",
                    chart_size=CHART_SIZE,  # type: ignore
                ),
            )
        with col12:
            st.markdown("##### Цены продажи")
            st.altair_chart(
                stocks_chart(
                    view_data.sell_prices,
                    x_shorthand=f"{X_AXIS}:Q",
                    y_shorthand=f"{Y_AXIS}:Q",
                    color_shorthand=f"{C_AXIS}:N",
                    chart_size=CHART_SIZE,  # type: ignore
                ),
            )

        st.markdown("#### Доступная информация о владении рынками")
        if view_data.shares.empty:
            st.write("Нет доступной информации")
        else:
            st.dataframe(view_data.shares.sort_values(["market", "position"]))
