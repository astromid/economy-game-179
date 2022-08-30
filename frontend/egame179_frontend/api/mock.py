import time
from pathlib import Path

import streamlit as st
import ujson

from egame179_frontend.api.models import PlayerState


@st.experimental_memo  # type: ignore
def mock_player_state() -> PlayerState:
    json_string = Path("frontend/egame179_frontend/api/player_mock.json").read_text()
    return PlayerState.parse_obj(ujson.loads(json_string))


def mock_auth(login: str, password: str) -> str | None:
    user: str | None = None
    match login, password:
        case "root", "root":
            user = "root"
        case "corp", "123":
            user = "corp"
        case "news", "12345":
            user = "news"
    return user


def mock_manufacturing(volume: int, market: str) -> bool:
    time.sleep(1)
    return True
