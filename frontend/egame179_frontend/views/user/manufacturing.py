from itertools import chain
from os import stat

import streamlit as st

from egame179_frontend.api.models import PlayerState

MAX_MARKETS_IN_ROW = 5


def manufacturing() -> None:
    state: PlayerState = st.session_state.game_state
    markets = state.markets

    n_rows = len(markets) // MAX_MARKETS_IN_ROW + 1
    if len(resources) % MAX_MARKETS_IN_ROW:
        n_rows -= 1

    st.markdown("## Производство")
    columns = chain(*[st.columns(MAX_MARKETS_IN_ROW) for _ in range(n_rows)])
    for col, res in zip(columns, resources):
        with col:
            st.metric(
                label=res,
                value=resources[res]["price"],
                delta=f"{resources[res]['delta']:.2%}",
            )

    with st.form("manufacturing_form"):
        market = st.selectbox("Целевой рынок", list(st.session_state.game_state.resources.keys()))
        volume = st.slider("Количество товаров", min_value=0, max_value=100)

        total_price = st.session_state.game_state.resources[market]["price"] * volume
        rest_balance = st.session_state.game_state.balance - total_price

        st.text(f"Цена производства: {total_price}, остаток баланса: {rest_balance}")
        st.form_submit_button("Отправить на производство", on_click=manufacturing_callback)


def manufacturing_callback():
    pass
