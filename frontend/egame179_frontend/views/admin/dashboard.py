import itertools
from dataclasses import dataclass
from datetime import timedelta
from typing import Any

import pandas as pd
import streamlit as st
from httpx import HTTPStatusError

from egame179_frontend.api import CycleAPI, MarketAPI, ModificatorAPI
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
    modificators: pd.DataFrame
    name2market: dict[str, int]


@st.cache_data(max_entries=1)
def _cache_view_data(
    cycle: dict[str, Any],
    player_ids: list[int],
    names: dict[int, str],
    sync_status: dict[int, bool],
    modificators: list[dict[str, Any]],
    name2market: dict[str, int],
) -> _ViewData:
    modificators_df = pd.DataFrame(modificators)
    if not modificators_df.empty:
        modificators_df["user"] = modificators_df["user"].map(names)
    return _ViewData(
        cycle=cycle,
        player_ids=player_ids,
        names=names,
        sync_status=sync_status,
        modificators=modificators_df,
        name2market=name2market,
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
            name2market={node["name"]: node_id for node_id, node in state.markets.nodes(data=True)},
        )

        _cycle_stats(view_data)
        _cycle_controls(view_data)
        st.markdown("---")
        col1, col2 = st.columns([1, 2])
        with col1:
            _cycle_parameters(view_data)
        with col2:
            _sync_status(view_data)
        st.markdown("---")
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
    danger_zone = st.checkbox("Danger zone")
    col1, col2, col3, _ = st.columns([1, 1, 1, 4])
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
        if danger_zone:
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


def _sync_status(view_data: _ViewData) -> None:
    st.markdown("#### Статус синхронизации игроков")
    columns = itertools.chain(*[st.columns(3) for _ in range(2)])
    for col, uid in zip(columns, view_data.player_ids):
        with col:
            if view_data.sync_status[uid]:
                st.success(view_data.names[uid])
            else:
                st.warning(view_data.names[uid])


def _modificators_control(view_data: _ViewData) -> None:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Текущие и будущие модификаторы")
        if view_data.modificators.empty:
            st.info("Нет активных и будущих модификаторов")
        else:
            st.dataframe(view_data.modificators)
    with col2:
        tab1, tab2 = st.tabs(["Комиссии", "Разблокировка"])
        with tab1:
            _create_fee_modificator(view_data)
        with tab2:
            _unlock_market(view_data)


def _create_fee_modificator(view_data: _ViewData) -> None:
    name2uid = {name: uid for uid, name in view_data.names.items()}
    st.markdown("#### Создание модификатора")
    cycle = st.radio(
        "Цикл модификатора",
        options=[0, view_data.cycle["id"] + 1, view_data.cycle["id"] + 2],
        horizontal=True,
    )
    user = st.selectbox(
        "Корпорация",
        options=[view_data.names[uid] for uid in view_data.player_ids],
        key="corporation_fee_modificator",
    )
    fee = st.selectbox("Комиссия (параметр)", options=["alpha", "beta", "gamma"])
    coeff = st.number_input("Коэффициент")
    if st.button("Создать", disabled=cycle == 0):
        try:
            ModificatorAPI.new(cycle=cycle, user=name2uid[user], fee=fee, coeff=coeff)  # type: ignore
        except HTTPStatusError as exc:
            st.error(f"Ошибка: {exc = }", icon="⚙")
        else:
            st.success("Модификатор создан", icon="👍")


def _unlock_market(view_data: _ViewData) -> None:
    name2uid = {name: uid for uid, name in view_data.names.items()}
    st.markdown("Разблокировка рынка")
    user = st.selectbox("Корпорация", options=[view_data.names[uid] for uid in view_data.player_ids])
    market = st.selectbox("Рынок", options=view_data.name2market.keys())
    if st.button("Разблокировать", disabled=view_data.cycle["ts_start"] is not None):
        try:
            MarketAPI.unlock_market(
                cycle=view_data.cycle["id"],
                user=name2uid[user],    # type: ignore
                market=view_data.name2market[market],    # type: ignore
            )
        except HTTPStatusError as exc:
            st.error(f"Ошибка: {exc = }", icon="⚙")
        else:
            st.success("Рынок разблокирован", icon="👍")
