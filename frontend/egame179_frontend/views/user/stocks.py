from dataclasses import dataclass

import pandas as pd
import streamlit as st

from egame179_frontend.api.models import PlayerState
from egame179_frontend.visualization import cycles_history_chart


@dataclass
class _ViewState:
    cycle: int
    player_stocks_df: pd.DataFrame
    npc_stocks_df: pd.DataFrame
    max_player_stock: float
    max_npc_stock: float


def stocks() -> None:
    state: PlayerState = st.session_state.game_state
    view_state = _cache_view_data(
        cycle=state.cycle,
        player_stocks=state.player_stocks,
        npc_stocks=state.npc_stocks,
    )
    _render_view(view_state)


@st.experimental_memo
def _cache_view_data(
    cycle: int,
    player_stocks: dict[str, list[float]],
    npc_stocks: dict[str, list[float]],
) -> _ViewState:
    player_stocks_df = pd.DataFrame(player_stocks)
    player_stocks_df["cycle"] = player_stocks_df.index

    npc_stocks_df = pd.DataFrame(npc_stocks)
    npc_stocks_df["cycle"] = npc_stocks_df.index
    return _ViewState(
        cycle=cycle,
        player_stocks_df=player_stocks_df.melt(id_vars="cycle", var_name="ticket", value_name="price"),
        npc_stocks_df=npc_stocks_df.melt(id_vars="cycle", var_name="ticket", value_name="price"),
        max_player_stock=player_stocks_df.drop("cycle", axis=1).max(),
        max_npc_stock=npc_stocks_df.drop("cycle", axis=1).max(),
    )


def _render_view(state: _ViewState) -> None:
    st.markdown("### Биржевые котировки")
    st.markdown(
        "<p style='text-align: center;'> Котировки акций корпораций </p>",
        unsafe_allow_html=True,
    )
    st.altair_chart(
        cycles_history_chart(
            state.player_stocks_df,
            x_shorthand="cycle:Q",
            y_shorthand="price:Q",
            color_shorthand=None,
            max_x=state.cycle,
            max_y=state.max_player_stock,
            width=1000,
            height=600,
        ),
    )

    st.markdown(
        "<p style='text-align: center;'> Котировки акций логистических компаний </p>",
        unsafe_allow_html=True,
    )
    st.altair_chart(
        cycles_history_chart(
            state.npc_stocks_df,
            x_shorthand="cycle:Q",
            y_shorthand="price:Q",
            color_shorthand=None,
            max_x=state.cycle,
            max_y=state.max_player_stock,
            width=1000,
            height=600,
        ),
    )
