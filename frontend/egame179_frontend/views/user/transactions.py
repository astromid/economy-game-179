import streamlit as st

from egame179_frontend.api.models import PlayerState


def transactions(state: PlayerState) -> None:
    st.markdown("## Транзакции по корпоративному счёту")
