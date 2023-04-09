from dataclasses import dataclass

import networkx as nx
import numpy as np
import pyecharts as pe
import streamlit as st

from egame179_frontend.api.user import UserRoles
from egame179_frontend.state.state import PlayerState
from egame179_frontend.views.registry import AppView, appview

TOOLTIP_JS_CODE = "".join(
    [
        "function(params){",
        "var bulletItem = (field, value) => ",
        "'<p>' + params.marker + ' ' + field + ' ' + '<b>' + value + '</b></p>';",
        "let tip = bulletItem('Цена производства', params.data.buy_price);",
        "tip += bulletItem('Цена продажи', params.data.sale_price);",
        "tip += bulletItem('Топ-1', params.data.top1);",
        "tip += bulletItem('Топ-2', params.data.top2);",
        "tip += bulletItem('Ожидаемый спрос', params.data.expected_demand);",
        "return tip;",
        "}",
    ],
)


def markets_view(state: PlayerState) -> None:
    st.markdown("## Граф рынков")

    with st.expander("Статус отдельных рынков"):
        st.text("TBD")


def make_markets_graph() -> pe.charts.Graph:
    pass


def get_node_size_px(demand: float, start_demand: float) -> float:
    return 30 * (np.log10(demand / start_demand) + 1)


@dataclass
class _ViewData:
    markets_graph: pe.charts.Graph | None


@st.cache_data(max_entries=1)
def _cache_view_data(nx_graph: nx.Graph) -> _ViewData:
    pe_graph = pe.charts.Graph()
    nodes = [
        {
            
        }
        for node in nx_graph.nodes
    ]


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
        state: PlayerState = st.session_state.game
        markets_graph = state.markets
        st.write(markets_graph)
