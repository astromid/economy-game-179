import math
from dataclasses import dataclass
from itertools import chain
from typing import Any

import streamlit as st

from egame179_frontend.api.user import UserRoles
from egame179_frontend.state import RootState
from egame179_frontend.views.registry import AppView, appview

MAX_METRICS_IN_ROW = 5


@dataclass
class _ViewData:
    cycle: int
    storage: dict[int, list[dict[str, Any]]]
    m_id2name: dict[int, str]
    name2m_id: dict[str, int]
    names: dict[int, str]


@st.cache_data(max_entries=1)
def _cache_view_data(
    cycle: dict[str, Any],
    storage: dict[int, list[dict[str, Any]]],
    m_id2name: dict[int, str],
    names: dict[int, str],
) -> _ViewData:
    return _ViewData(
        cycle=cycle["id"],
        storage=storage,
        m_id2name=m_id2name,
        name2m_id={market: m_id for m_id, market in m_id2name.items()},
        names=names,
    )


@appview
class RootStorageView(AppView):
    """Storage AppView."""

    idx = 2
    name = "Склады и поставки"
    icon = "box-seam"
    roles = (UserRoles.ROOT.value,)

    def render(self) -> None:
        """Render view."""
        state: RootState = st.session_state.game
        view_data = _cache_view_data(
            cycle=state.cycle.dict(),
            storage=state.storage,
            m_id2name={node_id: node["name"] for node_id, node in state.markets.nodes.items()},
            names=state.names,
        )

        st.markdown("## Склады")
        _storage_block(storage=view_data.storage, m_id2name=view_data.m_id2name, names=view_data.names)


def _storage_block(
    storage: dict[int, list[dict[str, Any]]],
    m_id2name: dict[int, str],
    names: dict[int, str],
) -> None:
    n_rows = math.ceil(len(storage) / MAX_METRICS_IN_ROW)
    st.markdown("#### Запасы на складах")
    columns = chain(*[st.columns(MAX_METRICS_IN_ROW) for _ in range(n_rows)])
    for col, m_id in zip(columns, storage):
        with col:
            st.write(f"Рынок {m_id2name[m_id]}")
            mstorage = storage[m_id]
            st.bar_chart(
                data={
                    "quantity": [st["quantity"] for st in mstorage],
                    "team": [names[st["user"]] for st in mstorage],
                },
                x="team",
                y="quantity",
            )
