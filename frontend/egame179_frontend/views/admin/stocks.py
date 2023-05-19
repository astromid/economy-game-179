from dataclasses import dataclass
from types import MappingProxyType

import pandas as pd
import streamlit as st

from egame179_frontend.api.user import UserRoles
from egame179_frontend.state.state import RootState
from egame179_frontend.views.registry import AppView, appview
from egame179_frontend.visualization import stocks_chart

X_AXIS = "cycle"
Y_AXIS = "price"
C_AXIS = "company"
CHART_SIZE = MappingProxyType({"width": 600, "height": 350})


@dataclass
class _ViewData:
    player_stocks: pd.DataFrame
    npc_stocks: pd.DataFrame


@st.cache_data(max_entries=1)
def _cache_view_data(stocks: pd.DataFrame, player_ids: list[int]) -> _ViewData:
    return _ViewData(
        player_stocks=stocks[stocks["user"].isin(player_ids)],
        npc_stocks=stocks[~stocks["user"].isin(player_ids)],
    )


@appview
class RootStocksView(AppView):
    """Stocks AppView."""

    idx = 3
    name = "Биржевые сводки"
    icon = "graph-up"
    roles = (UserRoles.ROOT.value,)

    def __init__(self) -> None:
        self.view_data: _ViewData | None = None

    def render(self) -> None:
        """Render view."""
        state: RootState = st.session_state.game
        view_data = _cache_view_data(stocks=state.stocks, player_ids=state.player_ids)

        st.markdown("## Биржевые котировки")
        st.markdown("#### Акции корпораций")
        st.altair_chart(
            stocks_chart(
                view_data.player_stocks,
                x_shorthand=f"{X_AXIS}:Q",
                y_shorthand=f"{Y_AXIS}:Q",
                color_shorthand=f"{C_AXIS}:N",
                chart_size=CHART_SIZE,  # type: ignore
            ),
        )
        st.markdown("#### Акции логистических компаний")
        st.altair_chart(
            stocks_chart(
                view_data.npc_stocks,
                x_shorthand=f"{X_AXIS}:Q",
                y_shorthand=f"{Y_AXIS}:Q",
                color_shorthand=f"{C_AXIS}:N",
                chart_size=CHART_SIZE,  # type: ignore
            ),
        )
