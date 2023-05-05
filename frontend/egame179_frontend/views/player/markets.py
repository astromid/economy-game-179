from copy import deepcopy
from dataclasses import dataclass
from types import MappingProxyType

import networkx as nx
import pandas as pd
import pyecharts as pe
import streamlit as st
from streamlit_echarts import st_pyecharts

from egame179_frontend.api.user import UserRoles
from egame179_frontend.state.state import PlayerState
from egame179_frontend.views.registry import AppView, appview
from egame179_frontend.visualization import markets_graph, stocks_chart

X_AXIS = "cycle"
Y_AXIS = "price"
C_AXIS = "market"
CHART_SIZE = MappingProxyType({"width": 800, "height": 350})


@dataclass
class _ViewData:
    name: str
    cycle: int
    markets_graph: pe.charts.Graph
    buy_prices: pd.DataFrame
    sell_prices: pd.DataFrame


@st.cache_data(max_entries=1)
def _cache_view_data(
    name: str,
    cycle: int,
    _nx_graph: nx.Graph,
    demand_factors: dict[int, float],
    prices: pd.DataFrame,
    owners: dict[str, dict[int, str]],
    unlocked_markets: list[int],
) -> _ViewData:
    last_prices = prices[prices["cycle"] == cycle].set_index("market_id")
    graph = deepcopy(_nx_graph)
    nodeid2name = {}
    for node_id, node in graph.nodes.items():
        node["buy"] = last_prices.loc[node_id, "buy"]
        node["sell"] = last_prices.loc[node_id, "sell"]
        node["demand_factor"] = demand_factors[node_id]
        node["top1"] = owners["top1"][node_id]
        node["top2"] = owners["top2"][node_id]
        nodeid2name[node_id] = node["name"]
    prices["market"] = prices["market_id"].map(nodeid2name)
    buy_df = prices[[X_AXIS, "buy", C_AXIS]].rename(columns={"buy": Y_AXIS})
    sell_df = prices[[X_AXIS, "sell", C_AXIS]].rename(columns={"sell": Y_AXIS})
    return _ViewData(
        name=name,
        cycle=cycle,
        markets_graph=markets_graph(nx_graph=graph, unlocked_markets=unlocked_markets),
        buy_prices=buy_df,
        sell_prices=sell_df,
    )


@appview
class MarketsView(AppView):
    """Markets AppView."""

    idx = 11
    name = "Рынки"
    icon = "pie-chart-fill"
    roles = (UserRoles.PLAYER.value,)

    def __init__(self) -> None:
        self.view_data: _ViewData | None = None

    def render(self) -> None:
        """Render view."""
        self.view_data = self._cache_view_data(st.session_state.game)

        st.markdown(f"## Аналитика по рынкам {self.view_data.name} Inc.")
        col01, col02 = st.columns([2, 3])
        with col01:
            st_pyecharts(self.view_data.markets_graph, height="600px")
        with col02:
            st.markdown("##### Цены производства")
            st.altair_chart(
                stocks_chart(
                    self.view_data.buy_prices,
                    x_shorthand=f"{X_AXIS}:Q",
                    y_shorthand=f"{Y_AXIS}:Q",
                    color_shorthand=f"{C_AXIS}:N",
                    chart_size=CHART_SIZE,  # type: ignore
                ),
            )
            st.markdown("##### Цены продажи")
            st.altair_chart(
                stocks_chart(
                    self.view_data.sell_prices,
                    x_shorthand=f"{X_AXIS}:Q",
                    y_shorthand=f"{Y_AXIS}:Q",
                    color_shorthand=f"{C_AXIS}:N",
                    chart_size=CHART_SIZE,  # type: ignore
                ),
            )

    def _cache_view_data(self, state: PlayerState) -> _ViewData:
        return _cache_view_data(
            name=st.session_state.user.name,
            cycle=state.cycle.cycle,
            _nx_graph=state.markets,
            # TODO: remove mockups
            demand_factors={node_id: 1.0 for node_id in state.markets.nodes},
            prices=state.prices,
            owners={
                "top1" : {node_id: "None" for node_id in state.markets.nodes},
                "top2" : {node_id: "None" for node_id in state.markets.nodes},
            },
            unlocked_markets=state.unlocked_markets,
        )
