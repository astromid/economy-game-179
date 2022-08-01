import pandas as pd
import streamlit as st

from egame179_frontend.api.states import PlayerState


@st.experimental_memo
def _mock_player_state() -> PlayerState:
    return PlayerState(
        cycle=1,
        stocks=pd.DataFrame(
            {
                "ticket": [
                    "SFT",
                    "AGX",
                    "COR",
                    "SFT",
                    "AGX",
                    "COR",
                    "SFT",
                    "AGX",
                    "COR",
                    "SFT",
                    "AGX",
                    "COR",
                ],
                "price": [0, 0, 1, 0.33, 0.66, 0.9, 0.35, 1.2, 0.9, 0.66, 0.33, 0],
                "cycle": [0, 0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3],
            },
        ),
    )
