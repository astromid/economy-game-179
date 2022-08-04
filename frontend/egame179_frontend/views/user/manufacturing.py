from itertools import chain

import streamlit as st

MAX_MARKETS_IN_ROW = 5


def manufacturing() -> None:
    st.markdown("## Производство")
    resources = st.session_state.game_state.resources
    n_rows = len(resources) // MAX_MARKETS_IN_ROW + 1
    if len(resources) % MAX_MARKETS_IN_ROW:
        n_rows -= 1

    columns = chain(*[st.columns(MAX_MARKETS_IN_ROW) for _ in range(n_rows)])
    for col, res in zip(columns, resources):
        with col:
            st.metric(
                label=res,
                value=resources[res]["price"],
                delta=f"{resources[res]['delta']:.2%}",
            )
    # выбирать рынок из списка, добавлять в план производства
    # вывести финальный план с затратами
    # отправка всего плана на производство
    st.markdown("### План производства на цикл")
    # выбор количества через slider
