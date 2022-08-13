from dataclasses import dataclass
from itertools import chain
from math import ceil

import streamlit as st

from egame179_frontend.api.models import PlayerState

MAX_METRICS_IN_ROW = 5


def storage() -> None:
    """Entry point for storage view."""
    state: PlayerState = st.session_state.game_state
    view_state = _cache_view_data(state.storage, gamma=state.params.gamma)
    _render_view(view_state)


@dataclass
class _ViewState:
    storage: dict[str, int]
    expected_expense: float
    n_rows: int


@st.experimental_memo  # type: ignore
def _cache_view_data(storage_status: dict[str, int], gamma: float) -> _ViewState:
    return _ViewState(
        storage=storage_status,
        expected_expense=sum(storage_status.values()) * gamma,
        n_rows=ceil(len(storage_status) / MAX_METRICS_IN_ROW),
    )


def _render_view(state: _ViewState) -> None:
    st.markdown("## Складское управление")
    columns = chain(*[st.columns(MAX_METRICS_IN_ROW) for _ in range(state.n_rows)])
    for col, (market, volume) in zip(columns, state.storage.items()):
        with col:
            st.metric(label=market, value=volume)

    st.markdown(f"### Ожидаемые расходы на хранение: {state.expected_expense:.2f}")
