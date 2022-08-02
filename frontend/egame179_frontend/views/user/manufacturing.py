import streamlit as st


def manufacturing() -> None:
    st.title("NoName Corporation")
    st.markdown("## Производство")
    resources = st.session_state.player_state.resources
    columns = st.columns(5)
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
