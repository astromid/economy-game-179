"""Connector with the backend API."""
from dataclasses import dataclass

import pandas as pd
import streamlit as st


@dataclass
class PlayerState:
    cycle: int
    stocks: pd.DataFrame


@dataclass
class GameState:
    cycle: str


# @st.experimental_memo
def _mock_player_state() -> PlayerState:
    return PlayerState(
        cycle=0,
        stocks=pd.DataFrame(
            {
                "ticket": ["A", "B", "C", "A", "B", "C", "A", "B", "C", "A", "B", "C"],
                "price": [0, 0, 1, 0.33, 0.66, 0.9, 0.35, 1.2, 0.9, 0.66, 0.33, 0],
                "cycle": [0, 0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3],
            },
        ),
    )
