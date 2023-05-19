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
C_AXIS = "market_name"
CHART_SIZE = MappingProxyType({"width": 600, "height": 350})


@dataclass
class _ViewData:
    player_name: str
    cycle: int
    markets_graph: pe.charts.Graph
    buy_prices: pd.DataFrame
    sell_prices: pd.DataFrame
    current_prices: pd.DataFrame


@st.cache_data(max_entries=1)
def _cache_view_data(
    player_name: str,
    player_id: int,
    cycle: int,
    _nx_graph: nx.Graph,
    prices: pd.DataFrame,
    unlocked_markets: list[int],
    shares: dict[tuple[int, int], tuple[int, float | None]],
    thetas: dict[int, float],
) -> _ViewData:
    market2name = {node_id: node["name"] for node_id, node in _nx_graph.nodes.items()}
    user2home = {node["home_user"]: node_id for node_id, node in _nx_graph.nodes.items()}

    prices["market_name"] = prices["market"].map(market2name)
    current_prices = prices[prices["cycle"] == cycle].copy()
    current_prices["theta"] = current_prices["market"].map(thetas)
    current_prices["buy_discount"] = current_prices["buy"] * (1 - current_prices["theta"])
    current_prices = current_prices[["market_name", "buy", "buy_discount", "sell"]]

    owned_markets = [market for market in _nx_graph.nodes if shares.get((market, 1), (None, None))[0] == player_id]
    pe_graph = markets_graph(
        nx_graph=_nx_graph,
        home=user2home[player_id],
        owned=owned_markets,
        unlocked=unlocked_markets,
    )
    return _ViewData(
        player_name=player_name,
        cycle=cycle,
        markets_graph=pe_graph,
        buy_prices=prices[[X_AXIS, "buy", C_AXIS]].rename(columns={"buy": Y_AXIS}),
        sell_prices=prices[[X_AXIS, "sell", C_AXIS]].rename(columns={"sell": Y_AXIS}),
        current_prices=current_prices,
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
            player_id=st.session_state.user.id,
            cycle=state.cycle.id,
            _nx_graph=state.detailed_markets,
            prices=state.prices.copy(),
            unlocked_markets=state.unlocked_markets,
            shares=state.shares,
            thetas=state.thetas,
        )

        st.markdown(f"## Аналитика по рынкам {view_data.player_name} Inc.")
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
