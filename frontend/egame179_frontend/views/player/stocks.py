from dataclasses import dataclass
from types import MappingProxyType

import pandas as pd
import streamlit as st

from egame179_frontend.models import PlayerState
from egame179_frontend.visualization import stocks_chart

X_AXIS = "cycle"
Y_AXIS = "price"
C_AXIS = "ticket"
CHART_SIZE = MappingProxyType({"width": 1000, "height": 600})


def stocks_view(state: PlayerState) -> None:
    """Entry point for stocks view.

    Args:
        state (PlayerState): PlayerState object.
    """
    view_state = _cache_view_data(
        cycle=state.cycle,
        player_stocks=state.stocks["players"],
        npc_stocks=state.stocks["npc"],
    )
    _render_view(view_state)


@dataclass
class _ViewState:
    cycle: int
    player_stocks_df: pd.DataFrame
    npc_stocks_df: pd.DataFrame


@st.experimental_memo  # type: ignore
def _cache_view_data(
    cycle: int,
    player_stocks: dict[str, list[float]],
    npc_stocks: dict[str, list[float]],
) -> _ViewState:
    player_stocks_df = pd.DataFrame(player_stocks)
    player_stocks_df[X_AXIS] = player_stocks_df.index + 1

    npc_stocks_df = pd.DataFrame(npc_stocks)
    npc_stocks_df[X_AXIS] = npc_stocks_df.index + 1
    return _ViewState(
        cycle=cycle,
        player_stocks_df=player_stocks_df.melt(id_vars=X_AXIS, var_name=C_AXIS, value_name=Y_AXIS),
        npc_stocks_df=npc_stocks_df.melt(id_vars=X_AXIS, var_name=C_AXIS, value_name=Y_AXIS),
    )


def _render_view(state: _ViewState) -> None:
    st.markdown("### Биржевые котировки")
    st.markdown("#### Акции корпораций")
    st.altair_chart(
        stocks_chart(
            state.player_stocks_df,
            x_shorthand=f"{X_AXIS}:Q",
            y_shorthand=f"{Y_AXIS}:Q",
            color_shorthand=f"{C_AXIS}:N",
            chart_size=CHART_SIZE,  # type: ignore
        ),
    )
    st.markdown("#### Акции логистических компаний")
    st.altair_chart(
        stocks_chart(
            state.npc_stocks_df,
            x_shorthand=f"{X_AXIS}:Q",
            y_shorthand=f"{Y_AXIS}:Q",
            color_shorthand=f"{C_AXIS}:N",
            chart_size=CHART_SIZE,  # type: ignore
        ),
    )
