from dataclasses import dataclass
from types import MappingProxyType

import networkx as nx
import pandas as pd
import pyecharts as pe
import streamlit as st
from streamlit_echarts import st_pyecharts

from egame179_frontend.api.user import UserRoles
from egame179_frontend.state import PlayerState
from egame179_frontend.views.registry import AppView, appview
from egame179_frontend.visualization import markets_graph, stocks_chart

X_AXIS = "cycle"
Y_AXIS = "price"
C_AXIS = "market"
CHART_SIZE = MappingProxyType({"width": 800, "height": 350})


@dataclass
class _ViewData:
    player_name: str
    cycle: int
    markets_graph: pe.charts.Graph
    buy_prices: pd.DataFrame
    sell_prices: pd.DataFrame


@st.cache_data(max_entries=1)
def _cache_view_data(
    player_name: str,
    cycle: int,
    _nx_graph: nx.Graph,
    prices: pd.DataFrame,
    unlocked_markets: list[int],
) -> _ViewData:
    m_id2name = {node_id: node["name"] for node_id, node in _nx_graph.nodes.items()}
    prices["market"] = prices["market_id"].map(m_id2name)
    buy_df = prices[[X_AXIS, "buy", C_AXIS]].rename(columns={"buy": Y_AXIS})
    sell_df = prices[[X_AXIS, "sell", C_AXIS]].rename(columns={"sell": Y_AXIS})
    return _ViewData(
        player_name=player_name,
        cycle=cycle,
        markets_graph=markets_graph(nx_graph=_nx_graph, unlocked_markets=unlocked_markets),
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

    def render(self) -> None:
        """Render view."""
        state: PlayerState = st.session_state.game
        view_data = _cache_view_data(
            player_name=st.session_state.user.name,
            cycle=state.cycle.cycle,
            _nx_graph=state.detailed_markets,
            prices=state.prices.copy(),
            unlocked_markets=state.unlocked_markets,
        )

        st.markdown(f"## Аналитика по рынкам {view_data.player_name} Inc.")
        col01, col02 = st.columns([2, 3])
        with col01:
            st_pyecharts(view_data.markets_graph, height="600px")
        with col02:
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
