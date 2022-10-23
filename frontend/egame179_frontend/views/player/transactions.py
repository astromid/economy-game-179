import pandas as pd
import streamlit as st

from egame179_frontend.models import PlayerState


def transactions_view(state: PlayerState) -> None:
    """Entry point for transactions view.

    Args:
        state (PlayerState): PlayerState object.
    """
    transactions = _cache_view_data([tr.dict() for tr in state.player.transactions])
    _render_view(transactions)


@st.experimental_memo  # type: ignore
def _cache_view_data(transactions: list[dict[str, int | float | str | None]]) -> pd.DataFrame:
    return pd.DataFrame(transactions)


def _render_view(transactions: pd.DataFrame) -> None:
    st.markdown("## Транзакции по корпоративному счёту")
    st.dataframe(transactions)
