import pandas as pd
import streamlit as st

from egame179_frontend.api.models import PlayerState


def transactions(state: PlayerState) -> None:
    """Entry point for transactions view.

    Args:
        state (PlayerState): PlayerState object.
    """
    st.markdown("## Транзакции по корпоративному счёту")


@st.experimental_memo  # type: ignore
def _cache_view_data(data: ) -> pd.DataFrame:
    return pd.DataFrame()
