import streamlit as st

from egame179_frontend.api.user import UserRoles
from egame179_frontend.state.state import PlayerState
from egame179_frontend.views.registry import AppView, appview


def sales_view(state: PlayerState) -> None:
    st.markdown("## Поставки")
    # В форме поставки должны отображаться только те товары, которые есть в наличии
    with st.expander("Активные поставки"):
        col1, col2, col3 = st.columns([1, 1, 3])
        with col1:
            st.text("Рынок 1")
            st.text("Рынок 2")
        with col2:
            st.text("50%")
            st.text("33%")
        with col3:
            st.progress(0.5)
            st.progress(0.33)


@appview
class SuppliesView(AppView):
    """Supplies AppView."""

    idx = 13
    name = "Склады и поставки"
    icon = "box-seam"
    roles = (UserRoles.PLAYER.value,)

    def __init__(self) -> None:
        self.view_data: _ViewData | None = None

    def render(self) -> None:
        """Render view."""
        state: PlayerState = st.session_state.game


MAX_METRICS_IN_ROW = 5


def storage_view(state: PlayerState) -> None:
    """Entry point for storage view.

    Args:
        state (PlayerState): PlayerState object.
    """
    view_state = _cache_view_data(
        cycle=state.cycle,
        storage_status={market: pm_info.storage for market, pm_info in state.player.products.items()},
        gamma=state.game_params.gamma,
    )
    _render_view(view_state)


@dataclass
class _ViewState:
    cycle: int
    storage: dict[str, int]
    storage_sum: int
    gamma: float
    expected_fee: float
    n_rows: int


@st.experimental_memo  # type: ignore
def _cache_view_data(
    cycle: int,
    storage_status: dict[str, int],
    gamma: float,
) -> _ViewState:
    storage_sum = sum(storage_status.values())
    return _ViewState(
        cycle=cycle,
        storage=storage_status,
        storage_sum=storage_sum,
        gamma=gamma,
        expected_fee=storage_sum * gamma,
        n_rows=ceil(len(storage_status) / MAX_METRICS_IN_ROW),
    )


def _render_view(state: _ViewState) -> None:
    st.markdown("## Складское управление")
    columns = chain(*[st.columns(MAX_METRICS_IN_ROW) for _ in range(state.n_rows)])
    for col, (market, volume) in zip(columns, state.storage.items()):
        with col:
            st.metric(label=market, value=volume)

    st.text(f"Суммарно товаров на складе: {state.storage_sum} шт.")
    st.text("Ожидаемые расходы на хранение в этом цикле:")
    st.text(f"{state.storage_sum} шт. x {state.gamma} = {state.expected_fee}")
