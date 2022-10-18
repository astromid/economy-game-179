import time
from pathlib import Path

import streamlit as st
import ujson

from egame179_frontend.api.models import PlayerState


@st.experimental_memo  # type: ignore
def mock_player_state() -> PlayerState:
    json_string = Path("egame179_frontend/api/player_mock.json").read_text()
    return PlayerState.parse_obj(ujson.loads(json_string))


def mock_manufacturing(volume: int, market: str) -> bool:
    time.sleep(1)
    return True
