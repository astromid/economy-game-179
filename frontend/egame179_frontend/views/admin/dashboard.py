from dataclasses import dataclass
from datetime import timedelta
from typing import Any

import streamlit as st
from httpx import HTTPStatusError

from egame179_frontend.api import CycleAPI, ModificatorAPI
from egame179_frontend.api.user import UserRoles
from egame179_frontend.settings import settings
from egame179_frontend.state.state import RootState
from egame179_frontend.views.registry import AppView, appview


@dataclass
class _ViewData:
    cycle: dict[str, Any]
    player_ids: list[int]
    names: dict[int, str]
    sync_status: dict[int, bool]
    modificators: list[dict[str, Any]]


@st.cache_data(max_entries=1)
def _cache_view_data(
    cycle: dict[str, Any],
    player_ids: list[int],
    names: dict[int, str],
    sync_status: dict[int, bool],
    modificators: list[dict[str, Any]],
) -> _ViewData:
    return _ViewData(
        cycle=cycle,
        player_ids=player_ids,
        names=names,
        sync_status=sync_status,
        modificators=modificators,
    )


@appview
class RootDashboard(AppView):
    """Root game dashboard AppView."""

    idx = 0
    name = "Управление"
    icon = "house"
    roles = (UserRoles.ROOT.value,)

    def render(self) -> None:
        """Render view."""
        state: RootState = st.session_state.game
        view_data = _cache_view_data(
            cycle=state.cycle.dict(),
            player_ids=state.player_ids,
            names=state.names,
            sync_status=state.sync_status,
            modificators=state.modificators,
        )

        col1, col2 = st.columns([2, 1], gap="medium")
        with col1:
            _cycle_stats(view_data)
            st.markdown("---")
            _cycle_controls(view_data)
        with col2:
            _cycle_parameters(view_data)

        _modificators_control(view_data)


def _cycle_stats(view_data: _ViewData) -> None:
    ts_start = view_data.cycle["ts_start"]
    if ts_start is not None:
        est_timedelta = timedelta(seconds=settings.estimated_cycle_time)
        cycle_start = ts_start.time().isoformat()
        cycle_end = (ts_start + est_timedelta).time().isoformat()
    else:
        cycle_start = "Ожидание"
        cycle_end = "Перерыв ~5 минут"

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Цикл #", value=view_data.cycle["id"])
    with col2:
        st.metric("Начался", value=cycle_start)
    with col3:
        st.metric("Ожидаемое время завершения", value=cycle_end)


def _cycle_controls(view_data: _ViewData) -> None:
    col1, col2, col3 = st.columns(2)
    with col1:
        st.button(
            "Начать цикл",
            on_click=CycleAPI.start_cycle,
            disabled=view_data.cycle["ts_start"] is not None,
        )
    with col2:
        st.button(
            "Завершить цикл",
            on_click=CycleAPI.finish_cycle,
            disabled=view_data.cycle["ts_start"] is None,
        )
    with col3:
        if st.button("! Реинициализация игры !"):
            # TODO: Remove before release!
            import subprocess
            result = subprocess.run(["./_reinit_db.sh"], stdout=subprocess.PIPE, text=True)
            st.write("stdout:", result.stdout)


def _cycle_parameters(view_data: _ViewData) -> None:
    st.markdown("#### Параметры цикла")
    st.write(f"Организационные расходы: {view_data.cycle['alpha']}")
    st.write(f"Комиссия за операции на рынке: {view_data.cycle['beta']}")
    st.write(f"Стоимость складского хранения: {view_data.cycle['gamma']}")
    st.write(f"Время полной поставки: {view_data.cycle['tau_s']} c")
    st.write(f"Кредитная ставка за овердрафт: {view_data.cycle['overdraft_rate']}")


def _modificators_control(view_data: _ViewData) -> None:
    name2uid = {name: uid for uid, name in view_data.names.items()}
    st.markdown("### Управление модификаторами")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Текущие модификаторы")
        for modificator in view_data.modificators:
            st.write(modificator)
    with col2:
        cycle = st.radio(
            "Цикл модификатора",
            options=[0, view_data.cycle["id"] + 1, view_data.cycle["id"] + 2],
        )
        user = st.selectbox("Корпорация", options=[view_data.names[uid] for uid in view_data.player_ids])
        fee = st.selectbox("Корпорация", options=["alpha", "beta", "gamma"])
        coeff = st.number_input("Коэффициент")
        if st.button("К А Р А", disabled=cycle == 0):
            try:
                ModificatorAPI.new(cycle=cycle, user=name2uid[user], fee=fee, coeff=coeff)  # type: ignore
            except HTTPStatusError as exc:
                st.error(f"Ошибка: {exc = }", icon="⚙")
            else:
                st.success("Кара отправлена")
