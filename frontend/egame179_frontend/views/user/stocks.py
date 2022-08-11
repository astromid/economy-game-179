from dataclasses import dataclass
from types import MappingProxyType

import pandas as pd
import streamlit as st

from egame179_frontend.api.models import PlayerState
from egame179_frontend.visualization import stocks_chart

X_AXIS = "cycle"
Y_AXIS = "price"
C_AXIS = "ticket"
CHART_SIZE = MappingProxyType({"width": 1000, "height": 600})


def stocks() -> None:
    state: PlayerState = st.session_state.game_state
    view_state = _cache_view_data(
        cycle=state.cycle,
        player_stocks=state.player_stocks,
        npc_stocks=state.npc_stocks,
    )
    _render_view(view_state)


@dataclass
class _ViewState:
    cycle: int
    player_stocks_df: pd.DataFrame
    npc_stocks_df: pd.DataFrame


@st.experimental_memo
def _cache_view_data(
    cycle: int,
    player_stocks: dict[str, list[float]],
    npc_stocks: dict[str, list[float]],
) -> _ViewState:
    player_stocks_df = pd.DataFrame(player_stocks)
    player_stocks_df[X_AXIS] = player_stocks_df.index
    player_stocks_df = player_stocks_df.melt(id_vars=X_AXIS, var_name=C_AXIS, value_name=Y_AXIS)

    npc_stocks_df = pd.DataFrame(npc_stocks)
    npc_stocks_df[X_AXIS] = npc_stocks_df.index
    npc_stocks_df = npc_stocks_df.melt(id_vars=X_AXIS, var_name=C_AXIS, value_name=Y_AXIS)

    return _ViewState(
        cycle=cycle,
        player_stocks_df=player_stocks_df,
        npc_stocks_df=npc_stocks_df,
    )


def _render_view(state: _ViewState) -> None:
    st.markdown("### Биржевые котировки")
    st.markdown(
        "<p style='text-align: center;'> Котировки акций корпораций </p>",
        unsafe_allow_html=True,
    )
    st.altair_chart(
        stocks_chart(
            state.player_stocks_df,
            x_shorthand=f"{X_AXIS}:Q",
            y_shorthand=f"{Y_AXIS}:Q",
            color_shorthand=f"{C_AXIS}:N",
            chart_size=CHART_SIZE,  # type: ignore
        ),
    )

    st.markdown(
        "<p style='text-align: center;'> Котировки акций логистических компаний </p>",
        unsafe_allow_html=True,
    )
    st.altair_chart(
        stocks_chart(
            state.npc_stocks_df,
            x_shorthand=f"{X_AXIS}:Q",
            y_shorthand=f"{Y_AXIS}:Q",
            color_shorthand=f"{C_AXIS}:N",
            chart_size=CHART_SIZE,  # type: ignore
        ),
    )
